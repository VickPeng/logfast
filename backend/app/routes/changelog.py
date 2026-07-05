"""
Repository management and changelog CRUD.
"""
import secrets
import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy import select, desc, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Repository, Changelog
from app.services.github import (
    list_user_repos,
    get_commits_since,
    get_latest_tag,
    create_webhook,
    delete_webhook,
    get_user_info,
)
from app.services.ai import generate_changelog

router = APIRouter()


# ── Pydantic Schemas ──────────────────────────────

class RepoCreate(BaseModel):
    github_repo_id: int
    full_name: str
    name: str
    description: str | None = None
    private: bool = False


class RepoResponse(BaseModel):
    id: int
    full_name: str
    name: str
    description: str | None = None
    private: bool
    custom_domain: str | None = None
    activated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChangelogResponse(BaseModel):
    id: int
    version: str | None
    title: str
    content: str
    status: str
    published_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class ChangelogGenerate(BaseModel):
    repo_id: int
    since: str | None = None  # ISO datetime string


# ── Helpers ────────────────────────────────────────

async def _get_user(db: AsyncSession, github_token: str) -> User:
    """Verify token and return user (read-only, no commit needed)."""
    user_info = await get_user_info(github_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid GitHub token")
    result = await db.execute(select(User).where(User.github_id == user_info["id"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── Repository Routes ──────────────────────────────

@router.get("/repos")
async def list_my_repos(
    github_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """List user's GitHub repos that can be connected."""
    repos = await list_user_repos(github_token)
    # Also fetch connected repos from DB
    user = await _get_user(db, github_token)
    result = await db.execute(
        select(Repository).where(
            Repository.user_id == user.id,
            Repository.activated == True,
        )
    )
    connected = {r.github_repo_id: r for r in result.scalars().all()}

    return [
        {
            "github_id": r["id"],
            "full_name": r["full_name"],
            "name": r["name"],
            "description": r.get("description"),
            "private": r["private"],
            "language": r.get("language"),
            "stars": r.get("stargazers_count"),
            "connected": r["id"] in connected,
            "connected_repo_id": connected[r["id"]].id if r["id"] in connected else None,
        }
        for r in repos
    ]


@router.post("/repos/connect", response_model=RepoResponse)
async def connect_repo(
    body: RepoCreate,
    github_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Connect a GitHub repo to LogFast."""
    user = await _get_user(db, github_token)

    # Check if already connected
    result = await db.execute(
        select(Repository).where(
            Repository.user_id == user.id,
            Repository.github_repo_id == body.github_repo_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.activated = True
        await db.commit()
        await db.refresh(existing)
        return existing

    # Create webhook for auto-changelog
    webhook_secret = secrets.token_urlsafe(32)
    webhook = await create_webhook(github_token, body.full_name, webhook_secret)

    repo = Repository(
        user_id=user.id,
        github_repo_id=body.github_repo_id,
        full_name=body.full_name,
        name=body.name,
        description=body.description,
        private=body.private,
        webhook_id=webhook["id"] if webhook else None,
        webhook_secret=webhook_secret,
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)
    return repo


@router.post("/repos/{repo_id}/disconnect")
async def disconnect_repo(
    repo_id: int,
    github_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect a repo."""
    user = await _get_user(db, github_token)
    result = await db.execute(
        select(Repository).where(
            Repository.id == repo_id,
            Repository.user_id == user.id,
        )
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Delete webhook (best-effort — if it fails, still proceed)
    if repo.webhook_id:
        try:
            await delete_webhook(github_token, repo.full_name, repo.webhook_id)
        except Exception as e:
            print(f"Disconnect: webhook delete failed (non-fatal): {e}")

    # Delete associated changelogs FIRST to avoid FK constraint violation
    await db.execute(
        sa_delete(Changelog).where(Changelog.repository_id == repo.id)
    )
    # Then delete the repo
    await db.delete(repo)
    await db.commit()
    return {"status": "ok"}


@router.get("/repos/connected", response_model=list[RepoResponse])
async def list_connected_repos(
    github_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """List all connected repos."""
    user = await _get_user(db, github_token)
    result = await db.execute(
        select(Repository)
        .where(Repository.user_id == user.id, Repository.activated == True)
        .order_by(desc(Repository.created_at))
    )
    return result.scalars().all()


# ── Changelog Routes ───────────────────────────────

@router.post("/changelogs/generate", response_model=ChangelogResponse)
async def create_changelog(
    body: ChangelogGenerate,
    github_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Generate a changelog from recent commits."""
    user = await _get_user(db, github_token)

    # Get repo
    result = await db.execute(
        select(Repository).where(
            Repository.id == body.repo_id,
            Repository.user_id == user.id,
        )
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Get commits since last changelog or specified time
    since_dt = None
    if body.since:
        since_dt = datetime.fromisoformat(body.since)
    else:
        # Use last published changelog's time
        last_result = await db.execute(
            select(Changelog)
            .where(Changelog.repository_id == repo.id, Changelog.status == "published")
            .order_by(desc(Changelog.published_at))
            .limit(1)
        )
        last_changelog = last_result.scalar_one_or_none()
        if last_changelog and last_changelog.published_at:
            since_dt = last_changelog.published_at

    # Fetch commits
    commits = await get_commits_since(github_token, repo.full_name, since_dt)
    version = await get_latest_tag(github_token, repo.full_name)

    # Generate with AI
    changelog_data = await generate_changelog(commits, version)

    # Save to DB
    changelog = Changelog(
        repository_id=repo.id,
        version=version,
        title=changelog_data["title"],
        content=changelog_data["markdown"],
        raw_commits=commits,
        status="draft",
    )
    db.add(changelog)
    await db.commit()
    await db.refresh(changelog)
    return changelog


@router.get("/changelogs/{repo_id}", response_model=list[ChangelogResponse])
async def list_changelogs(
    repo_id: int,
    github_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """List changelogs for a repo."""
    user = await _get_user(db, github_token)
    result = await db.execute(
        select(Repository).where(
            Repository.id == repo_id,
            Repository.user_id == user.id,
        )
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    result = await db.execute(
        select(Changelog)
        .where(Changelog.repository_id == repo_id)
        .order_by(desc(Changelog.created_at))
    )
    return result.scalars().all()


@router.post("/changelogs/{changelog_id}/publish")
async def publish_changelog(
    changelog_id: int,
    github_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Publish a draft changelog."""
    user = await _get_user(db, github_token)
    result = await db.execute(
        select(Changelog).join(Repository).where(
            Changelog.id == changelog_id,
            Repository.user_id == user.id,
        )
    )
    changelog = result.scalar_one_or_none()
    if not changelog:
        raise HTTPException(status_code=404, detail="Changelog not found")

    changelog.status = "published"
    changelog.published_at = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "ok"}


class ChangelogUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


@router.patch("/changelogs/{changelog_id}/edit", response_model=ChangelogResponse)
async def update_changelog(
    changelog_id: int,
    body: ChangelogUpdate,
    github_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Update a draft changelog's title and/or content."""
    user = await _get_user(db, github_token)
    result = await db.execute(
        select(Changelog).join(Repository).where(
            Changelog.id == changelog_id,
            Repository.user_id == user.id,
        )
    )
    changelog = result.scalar_one_or_none()
    if not changelog:
        raise HTTPException(status_code=404, detail="Changelog not found")

    if body.title is not None:
        changelog.title = body.title
    if body.content is not None:
        changelog.content = body.content

    await db.commit()
    return changelog


@router.get("/public/{repo_full_name:path}")
async def public_changelog(
    repo_full_name: str,
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — anyone can view a repo's changelog."""
    result = await db.execute(
        select(Repository).where(
            Repository.full_name == repo_full_name,
            Repository.activated == True,
        )
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    result = await db.execute(
        select(Changelog)
        .where(Changelog.repository_id == repo.id, Changelog.status == "published")
        .order_by(desc(Changelog.published_at))
        .limit(limit)
    )
    changelogs = result.scalars().all()

    return {
        "repo": {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
        },
        "changelogs": [
            {
                "id": c.id,
                "version": c.version,
                "title": c.title,
                "content": c.content,
                "published_at": c.published_at.isoformat() if c.published_at else None,
            }
            for c in changelogs
        ],
    }
