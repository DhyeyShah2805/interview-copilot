"""
Auth routes: register, login, refresh.

Returns JWT access + refresh tokens. The frontend stores them in httpOnly
cookies (preferred) or memory. Don't put them in localStorage.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    JWTError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TokenPair, UserCreate, UserLogin, UserRead

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenPair:
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(refresh_token: str, db: AsyncSession = Depends(get_db)) -> TokenPair:
    try:
        claims = decode_token(refresh_token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

    if claims.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type")

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Malformed token")

    return TokenPair(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )
