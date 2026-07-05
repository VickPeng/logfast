"""
GitHub API service — OAuth, repo listing, commit fetching, webhook setup.
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional

import httpx
from app.config import settings


GITHUB_API = "https://api.github.com"
GITHUB_OAUTH = "https://github.com/login/oauth"


def get_oauth_url(state: str = None) -> str:
    """Generate GitHub OAuth authorization URL."""
    if state is None:
        state = secrets.token_urlsafe(16)
    return (
        f"{GITHUB_OAUTH}/authorize"
        f"?client_id={settings.github_client_id}"
        f"&redirect_uri={settings.api_base_url}/api/auth/github/callback"
        f"&scope=repo,user:email"
        f"&state={state}"
    )


async def exchange_code(code: str) -> Optional[dict]:
    """Exchange OAuth code for access token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GITHUB_OAUTH}/access_token",
            json={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": f"{settings.api_base_url}/api/auth/github/callback",
            },
            headers={"Accept": "application/json"},
        )
        if resp.status_code != 200:
            print(f"GitHub OAuth exchange failed: status={resp.status_code}, body={resp.text}")
            return None
        data = resp.json()
        # GitHub returns 200 even for errors, check body for error field
        if "error" in data:
            print(f"GitHub OAuth error: {data.get('error')} — {data.get('error_description')}")
            return None
        return data


async def get_user_info(token: str) -> Optional[dict]:
    """Fetch authenticated user info."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        if resp.status_code != 200:
            return None
        return resp.json()


async def get_user_emails(token: str) -> list[dict]:
    """Fetch user's email addresses."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/user/emails",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        if resp.status_code != 200:
            return []
        return resp.json()


async def list_user_repos(token: str, page: int = 1, per_page: int = 30) -> list[dict]:
    """List repos accessible to the user (with push access)."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/user/repos",
            params={"sort": "updated", "per_page": per_page, "page": page, "type": "owner"},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        if resp.status_code != 200:
            return []
        return resp.json()


async def get_commits_since(
    token: str, full_name: str, since: Optional[datetime] = None, max_count: int = 50
) -> list[dict]:
    """Get commits for a repo, optionally since a specific time."""
    params = {"per_page": min(max_count, 100)}
    if since:
        params["since"] = since.isoformat() + "Z"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{full_name}/commits",
            params=params,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        if resp.status_code != 200:
            return []

        commits = resp.json()
        result = []
        for c in commits[:max_count]:
            result.append({
                "sha": c["sha"],
                "message": c["commit"]["message"],
                "author": c["commit"]["author"]["name"] if c["commit"].get("author") else "unknown",
                "date": c["commit"]["author"]["date"] if c["commit"].get("author") else None,
            })
        return result


async def get_latest_tag(token: str, full_name: str) -> Optional[str]:
    """Get the latest tag/version for a repo."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{full_name}/tags",
            params={"per_page": 1},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        if resp.status_code != 200:
            return None
        tags = resp.json()
        return tags[0]["name"] if tags else None


async def create_webhook(
    token: str, full_name: str, secret: str
) -> Optional[dict]:
    """Create a push webhook for a repository."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GITHUB_API}/repos/{full_name}/hooks",
            json={
                "name": "web",
                "active": True,
                "events": ["push"],
                "config": {
                    "url": f"{settings.api_base_url}/api/webhook/github",
                    "content_type": "json",
                    "secret": secret,
                },
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        if resp.status_code not in (200, 201):
            return None
        return resp.json()


async def delete_webhook(token: str, full_name: str, webhook_id: int) -> bool:
    """Delete a webhook."""
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{GITHUB_API}/repos/{full_name}/hooks/{webhook_id}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        return resp.status_code == 204


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook HMAC signature."""
    if not signature:
        return False
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
