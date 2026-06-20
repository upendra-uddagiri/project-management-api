from fastapi import APIRouter, status, Depends, UploadFile, File, BackgroundTasks
from app.schemas.task import TaskRead, TaskUpdate
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.project import Project, ProjectMember
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from pydantic import BaseModel
from app.services.task_services import notify_assignee
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
import uuid
import os


class AssignTaskRequest(BaseModel):
    assignee_id: str


router = APIRouter(prefix="/tasks", tags=["tasks"])
UPLOAD_DIR = "uploads"


async def check_task_access(task: Task, current_user: User, db: AsyncSession):
    result = await db.execute(select(Project).where(Project.id == task.project_id))
    project = result.scalar_one_or_none()

    is_owner = project.owner_id == current_user.id
    member_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user.id
        )
    )
    is_member = member_result.scalar_one_or_none() is not None

    if not is_owner and not is_member:
        raise ForbiddenException(detail="Not authorized")


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NotFoundException(detail="Task not found")

    await check_task_access(task, current_user, db)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NotFoundException(detail="Task not found")

    await check_task_access(task, current_user, db)

    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NotFoundException(detail="Task not found")

    await check_task_access(task, current_user, db)
    await db.delete(task)
    await db.commit()


@router.post("/{task_id}/assign", response_model=TaskRead)
async def assign_task(
    task_id: str,
    assign_data: AssignTaskRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NotFoundException(detail="Task not found")

    await check_task_access(task, current_user, db)

    result = await db.execute(select(User).where(User.id == assign_data.assignee_id))
    assignee = result.scalar_one_or_none()
    if not assignee:
        raise NotFoundException(detail="User not found")

    task.assignee_id = assign_data.assignee_id
    await db.commit()
    await db.refresh(task)

    background_tasks.add_task(notify_assignee, assignee.email, task.title)
    return task


@router.post("/{task_id}/attachments")
async def upload_attachment(
    task_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NotFoundException(detail="Task not found")

    await check_task_access(task, current_user, db)

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "original_filename": file.filename,
        "saved_filename": unique_filename,
        "url": f"/uploads/{unique_filename}",
        "size_bytes": len(contents)
    }