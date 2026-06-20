from fastapi import Request
from fastapi.responses import JSONResponse


# custom exception classes
class NotFoundException(Exception):
    def __init__(self, detail: str = "Resource not found"):
        self.status_code = 404
        self.detail = detail


class ForbiddenException(Exception):
    def __init__(self, detail: str = "Not authorized"):
        self.status_code = 403
        self.detail = detail


class BadRequestException(Exception):
    def __init__(self, detail: str = "Bad request"):
        self.status_code = 400
        self.detail = detail


class UnauthorizedException(Exception):
    def __init__(self, detail: str = "Not authenticated"):
        self.status_code = 401
        self.detail = detail


# exception handlers
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def forbidden_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def bad_request_handler(request: Request, exc: BadRequestException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )