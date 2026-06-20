import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

# rate limiter instance — shared across the app
limiter = Limiter(key_func=get_remote_address)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        end_time = time.time()
        duration_ms = round((end_time - start_time) * 1000, 2)

        print(
            f"[{request.method}] {request.url.path} "
            f"-> {response.status_code} "
            f"({duration_ms}ms)"
        )

        return response