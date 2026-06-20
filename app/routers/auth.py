from fastapi import APIRouter, Depends, status,Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import get_db
from app.schemas.user import UserCreate, UserRead
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from pydantic import BaseModel
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    UnauthorizedException
)
from app.core.middleware import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # ... existing code unchanged
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise BadRequestException(detail="Email already registered")

    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # ... existing code unchanged
    result = await db.execute(select(User).where(User.email == form_data.username))
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise UnauthorizedException(detail="Invalid credentials")

    if not verify_password(form_data.password, existing_user.hashed_password):
        raise UnauthorizedException(detail="Invalid credentials")

    access_token = create_access_token({"sub": str(existing_user.id)})
    refresh_token = create_refresh_token({"sub": str(existing_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(token_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(token_data.refresh_token)
    user_id: str = payload.get("sub")

    if user_id is None:
        raise UnauthorizedException(detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundException(detail="User not found")

    new_access_token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }