from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import auth, users, projects, tasks
from app.routers.comments import task_comment_router, comment_router
from app.core.middleware import LoggingMiddleware, limiter
from app.core.exceptions import (
    NotFoundException, not_found_handler,
    ForbiddenException, forbidden_handler,
    BadRequestException, bad_request_handler,
    UnauthorizedException, unauthorized_handler
)

app = FastAPI(
    title="Project Management API",
    description="A RESTful API for managing projects, tasks, and teams",
    version="1.0.0",
)

# attach limiter to app state
app.state.limiter = limiter

# register middlewares
app.add_middleware(LoggingMiddleware)

# register rate limit exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# register custom exception handlers
app.add_exception_handler(NotFoundException, not_found_handler)
app.add_exception_handler(ForbiddenException, forbidden_handler)
app.add_exception_handler(BadRequestException, bad_request_handler)
app.add_exception_handler(UnauthorizedException, unauthorized_handler)

# register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(task_comment_router)
app.include_router(comment_router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
async def health():
    return {"status": "ok"}