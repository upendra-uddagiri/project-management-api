from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.dependencies import get_db, get_current_user
from app.utils.pagination import paginate
from app.models.project import Project, ProjectMember
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead, ProjectMemberRead
from pydantic import BaseModel
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskRead
from datetime import datetime
from app.core.exceptions import (
    NotFoundException,
    ForbiddenException,
    BadRequestException
)


class AddMemberRequest(BaseModel):
    user_id: str
    role: UserRole = UserRole.member


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/", response_model=List[ProjectRead])
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pagination: tuple = Depends(paginate)
):
    offset, limit = pagination
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == current_user.id)
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException(detail="Project not found")
    if project.owner_id != current_user.id:
        raise ForbiddenException(detail="Not authorized")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException(detail="Project not found")
    if project.owner_id != current_user.id:
        raise ForbiddenException(detail="Not authorized")

    for key, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException(detail="Project not found")
    if project.owner_id != current_user.id:
        raise ForbiddenException(detail="Not authorized")

    await db.delete(project)
    await db.commit()


@router.post("/{project_id}/members", response_model=ProjectMemberRead, status_code=status.HTTP_201_CREATED)
async def add_member(
    project_id: str,
    member_data: AddMemberRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException(detail="Project not found")
    if project.owner_id != current_user.id:
        raise ForbiddenException(detail="Not authorized")

    result = await db.execute(select(User).where(User.id == member_data.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException(detail="User not found")

    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_data.user_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise BadRequestException(detail="User is already a member")

    membership = ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id,
        role=member_data.role
    )
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    project_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException(detail="Project not found")
    if project.owner_id != current_user.id:
        raise ForbiddenException(detail="Not authorized")

    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise NotFoundException(detail="Member not found")

    await db.delete(membership)
    await db.commit()


@router.post("/{project_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def add_task(
    project_id: str,
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException(detail="Project not found")

    is_owner = project.owner_id == current_user.id
    member_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        )
    )
    is_member = member_result.scalar_one_or_none() is not None
    if not is_owner and not is_member:
        raise ForbiddenException(detail="Not authorized")

    task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        project_id=project_id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/{project_id}/tasks", response_model=List[TaskRead])
async def get_tasks(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pagination: tuple = Depends(paginate),
    status: Optional[TaskStatus] = None,
    assignee_id: Optional[str] = None,
    due_date_from: Optional[datetime] = None,
    due_date_to: Optional[datetime] = None,
    sort_by: Optional[str] = "created_at",
    order: Optional[str] = "asc",
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException(detail="Project not found")

    is_owner = project.owner_id == current_user.id
    member_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        )
    )
    is_member = member_result.scalar_one_or_none() is not None
    if not is_owner and not is_member:
        raise ForbiddenException(detail="Not authorized")

    query = select(Task).where(Task.project_id == project_id)

    if status is not None:
        query = query.where(Task.status == status)
    if assignee_id is not None:
        query = query.where(Task.assignee_id == assignee_id)
    if due_date_from is not None:
        query = query.where(Task.due_date >= due_date_from)
    if due_date_to is not None:
        query = query.where(Task.due_date <= due_date_to)

    if not hasattr(Task, sort_by):
        raise BadRequestException(detail=f"Invalid sort field: {sort_by}")

    sort_column = getattr(Task, sort_by)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    offset, limit = pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()