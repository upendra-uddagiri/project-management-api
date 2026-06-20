from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.dependencies import get_current_user, get_db, require_role
from app.schemas.user import UserRead, UserUpdate
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.utils.pagination import paginate
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.email is not None:
        current_user.email = user_data.email
    if user_data.password is not None:
        current_user.hashed_password = hash_password(user_data.password)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin))
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException(detail="User not found")
    return user


@router.get("", response_model=List[UserRead])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
    pagination: tuple = Depends(paginate)
):
    offset, limit = pagination
    result = await db.execute(select(User).offset(offset).limit(limit))
    return result.scalars().all()