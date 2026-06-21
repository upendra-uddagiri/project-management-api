from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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
    description="A RESTful API for managing projects, tasks and teams",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # tighten this in production e.g. ["http://localhost:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Logging middleware ────────────────────────────────────────────────────────
app.add_middleware(LoggingMiddleware)

# ── Custom exception handlers ─────────────────────────────────────────────────
app.add_exception_handler(NotFoundException,    not_found_handler)
app.add_exception_handler(ForbiddenException,   forbidden_handler)
app.add_exception_handler(BadRequestException,  bad_request_handler)
app.add_exception_handler(UnauthorizedException, unauthorized_handler)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(task_comment_router)
app.include_router(comment_router)

# ── Static files ──────────────────────────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
async def health():
    return {"status": "ok"}