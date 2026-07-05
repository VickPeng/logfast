"""
GitHub webhook handler — automatically triggers changelog generation on push.
"""
import json
import hmac
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Repository, Changelog
from app.services.ai import generate_changelog
from app.services.github import verify_webhook_signature

router = APIRouter()


@router.post("/github")
async def github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle GitHub push webhook event."""
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    event = request.headers.get("X-GitHub-Event", "")

    if event != "push":
        return {"status": "ignored", "event": event}

    # Parse payload to find repo
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    full_name = data.get("repository", {}).get("full_name")
    if not full_name:
        raise HTTPException(status_code=400, detail="No repo info")

    # Find connected repo
    result = await db.execute(
        select(Repository).where(
            Repository.full_name == full_name,
            Repository.activated == True,
        )
    )
    repo = result.scalar_one_or_none()
    if not repo:
        return {"status": "not_connected"}

    # Verify signature if we have a secret
    if repo.webhook_secret:
        if not verify_webhook_signature(payload, signature, repo.webhook_secret):
            raise HTTPException(status_code=403, detail="Invalid signature")

    # Extract commits from the push
    commits = []
    for c in data.get("commits", [])[:50]:
        commits.append({
            "sha": c["id"],
            "message": c["message"],
            "author": c["author"]["name"],
            "date": c["timestamp"],
        })

    if not commits:
        return {"status": "no_commits"}

    # Generate changelog
    changelog_data = await generate_changelog(commits)

    # Save as draft
    changelog = Changelog(
        repository_id=repo.id,
        title=changelog_data["title"],
        content=changelog_data["markdown"],
        raw_commits=commits,
        status="draft",
    )
    db.add(changelog)
    await db.commit()

    return {
        "status": "generated",
        "changelog_id": changelog.id,
        "title": changelog.title,
    }
