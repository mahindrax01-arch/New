from collections import defaultdict, deque
from dataclasses import dataclass
from math import ceil
from time import monotonic

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


@dataclass(frozen=True)
class RateLimitRule:
    path_prefix: str
    methods: frozenset[str]
    limit: int
    window_seconds: int


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "cross-origin")
        response.headers.setdefault("Cache-Control", "no-store")
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rules: list[RateLimitRule]):
        super().__init__(app)
        self.rules = rules
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def _hit(self, key: str, limit: int, window_seconds: int) -> int | None:
        now = monotonic()
        bucket = self._buckets[key]
        while bucket and now - bucket[0] >= window_seconds:
            bucket.popleft()

        if len(bucket) >= limit:
            retry_after = ceil(window_seconds - (now - bucket[0]))
            return max(retry_after, 1)

        bucket.append(now)
        return None

    async def dispatch(self, request: Request, call_next):
        client_host = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method.upper()

        for rule in self.rules:
            if path.startswith(rule.path_prefix) and method in rule.methods:
                retry_after = self._hit(
                    key=f"{client_host}:{method}:{rule.path_prefix}",
                    limit=rule.limit,
                    window_seconds=rule.window_seconds,
                )
                if retry_after is not None:
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={"detail": "Too many requests. Please slow down and try again."},
                        headers={"Retry-After": str(retry_after)},
                    )

        return await call_next(request)
