from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentRead
from app.core.exceptions import NotFoundException, ForbiddenException

task_comment_router = APIRouter(prefix="/tasks", tags=["comments"])
comment_router = APIRouter(prefix="/comments", tags=["comments"])


@task_comment_router.post("/{task_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: str,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NotFoundException(detail="Task not found")

    comment = Comment(
        content=comment_data.content,
        task_id=task_id,
        author_id=current_user.id
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@task_comment_router.get("/{task_id}/comments", response_model=List[CommentRead])
async def get_comments(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NotFoundException(detail="Task not found")

    result = await db.execute(select(Comment).where(Comment.task_id == task_id))
    return result.scalars().all()


@comment_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise NotFoundException(detail="Comment not found")

    if comment.author_id != current_user.id:
        raise ForbiddenException(detail="Not authorized")

    await db.delete(comment)
    await db.commit()