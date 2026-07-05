"""
GitHub OAuth authentication routes.
"""
import secrets
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.config import settings
from app.database import get_db
from app.models import User
from app.services.github import (
    get_oauth_url,
    exchange_code,
    get_user_info,
    get_user_emails,
)

router = APIRouter()


class UserResponse(BaseModel):
    id: int
    github_login: str
    github_avatar: str | None = None
    plan: str

    class Config:
        from_attributes = True


@router.get("/login")
async def login(request: Request):
    """Redirect user to GitHub OAuth."""
    state = secrets.token_urlsafe(16)
    # Derive redirect_uri from the request itself so it works in both dev and prod
    redirect_uri = str(request.base_url).rstrip("/") + "/api/auth/github/callback"
    url = get_oauth_url(state, redirect_uri=redirect_uri)
    # Store state in a cookie or cache in production
    # For MVP, we just redirect
    return RedirectResponse(url=url)


@router.get("/github/callback")
async def github_callback(
    code: str = Query(...),
    state: str = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle GitHub OAuth callback."""
    import traceback
    try:
        redirect_uri = str(request.base_url).rstrip("/") if request else settings.api_base_url + "/api/auth/github/callback"

        # Exchange code for token
        token_data = await exchange_code(code, redirect_uri=redirect_uri)
        if not token_data or "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to exchange code")

        access_token = token_data["access_token"]

        # Get user info
        user_info = await get_user_info(access_token)
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        # Get email
        emails = await get_user_emails(access_token)
        primary_email = next(
            (e["email"] for e in emails if e.get("primary")),
            emails[0]["email"] if emails else None
        )

        # Upsert user
        result = await db.execute(
            select(User).where(User.github_id == user_info["id"])
        )
        user = result.scalar_one_or_none()

        if user:
            user.github_token = access_token
            user.github_login = user_info["login"]
            user.github_avatar = user_info.get("avatar_url")
            user.github_email = primary_email
        else:
            user = User(
                github_id=user_info["id"],
                github_login=user_info["login"],
                github_email=primary_email,
                github_avatar=user_info.get("avatar_url"),
                github_token=access_token,
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)

        frontend_url = f"{settings.frontend_url}/auth/callback?token={access_token}&user_id={user.id}"
        return RedirectResponse(url=frontend_url)
    except HTTPException:
        raise
    except Exception as e:
        print(f"OAUTH CALLBACK ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OAuth failed: {e}")


@router.get("/me")
async def get_me(
    github_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Get current user info from token."""
    user_info_data = await get_user_info(github_token)
    if not user_info_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(User).where(User.github_id == user_info_data["id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=user.id,
        github_login=user.github_login,
        github_avatar=user.github_avatar,
        plan=user.plan,
    )
