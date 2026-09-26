"""FastAPI application and bounded, privacy-safe HTTP boundary."""

import json
import ipaddress
import logging
import os
import secrets
import threading
import time
from collections import OrderedDict, deque
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from .routes.analysis import router

MAX_REQUEST_BYTES = 2 * 1024 * 1024
MAX_MULTIPART_REQUEST_BYTES = 6 * 1024 * 1024
logger = logging.getLogger("resume.api")


def error_response(status, code, message, details=None, headers=None):
    return JSONResponse(
        {"error": {"code": code, "message": message, "details": details or []}},
        status_code=status,
        headers=headers,
    )


def _is_loopback_host(host: str) -> bool:
    normalized_host = host.strip().lower().strip("[]")
    if normalized_host == "localhost":
        return True
    try:
        return ipaddress.ip_address(normalized_host).is_loopback
    except ValueError:
        return False


def validate_deployment_security(host: str | None = None) -> None:
    if os.getenv("RESUME_API_KEY", ""):
        return
    anonymous_opt_in = os.getenv("ALLOW_UNAUTHENTICATED_POSTS", "").strip().lower()
    if anonymous_opt_in in {"1", "true", "yes", "on"}:
        return
    if host is None:
        raise RuntimeError(
            "Application factories require an explicit bind host, RESUME_API_KEY, "
            "or ALLOW_UNAUTHENTICATED_POSTS=true."
        )
    if _is_loopback_host(host):
        return
    raise RuntimeError(
        "Public API binding requires RESUME_API_KEY or explicit ALLOW_UNAUTHENTICATED_POSTS=true."
    )


class RequestRateLimiter:
    """Per-process limiter; expired clients are discarded and memory is bounded."""

    def __init__(self, limit: int, window_seconds: int, max_clients: int = 10000):
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_clients = max_clients
        self._requests = OrderedDict()
        self._lock = threading.Lock()

    def allow(self, client_id: str, now: float | None = None) -> bool:
        current_time = time.monotonic() if now is None else now
        cutoff = current_time - self.window_seconds
        with self._lock:
            while self._requests:
                first = next(iter(self._requests))
                if self._requests[first][-1] > cutoff:
                    break
                self._requests.pop(first)
            if client_id not in self._requests:
                if len(self._requests) >= self.max_clients:
                    return False
                self._requests[client_id] = deque()
            requests = self._requests[client_id]
            while requests and requests[0] <= cutoff:
                requests.popleft()
            if len(requests) >= self.limit:
                return False
            requests.append(current_time)
            self._requests.move_to_end(client_id)
            return True


class RequestBoundary:
    """Bound actual request bytes before parsing, including chunked requests.

    Generate request IDs locally and log only method, matched route, status and
    duration. Never log raw paths, query strings, bodies or exception messages.
    """

    def __init__(self, app, limiter):
        self.app = app
        self.limiter = limiter

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request_id = uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        started = time.monotonic()
        status = 500
        response_started = False

        async def tracked_send(message):
            nonlocal status, response_started
            if message["type"] == "http.response.start":
                status = message["status"]
                response_started = True
                message["headers"] = list(message.get("headers", [])) + [(b"x-request-id", request_id.encode())]
            await send(message)

        try:
            if scope["method"] == "POST":
                client = scope.get("client")
                if not self.limiter.allow(client[0] if client else "unknown"):
                    return await error_response(
                        429,
                        "rate_limited",
                        "Too many requests. Try again shortly.",
                        headers={"Retry-After": str(self.limiter.window_seconds)},
                    )(scope, receive, tracked_send)
                headers = dict(scope["headers"])
                configured_key = os.getenv("RESUME_API_KEY", "")
                token = headers.get(b"authorization", b"")
                if configured_key and not secrets.compare_digest(token, b"Bearer " + configured_key.encode()):
                    return await error_response(
                        401,
                        "unauthorized",
                        "A valid bearer token is required.",
                        headers={"WWW-Authenticate": "Bearer"},
                    )(scope, receive, tracked_send)
                try:
                    declared_size = int(headers.get(b"content-length", b"0"))
                    if declared_size < 0:
                        raise ValueError
                except ValueError:
                    return await error_response(400, "invalid_request", "Invalid Content-Length.")(
                        scope,
                        receive,
                        tracked_send,
                    )
                content_type = headers.get(b"content-type", b"")
                request_limit = (
                    MAX_MULTIPART_REQUEST_BYTES
                    if content_type.startswith(b"multipart/form-data")
                    else MAX_REQUEST_BYTES
                )
                body = bytearray()
                if declared_size > request_limit:
                    return await self.too_large(scope, receive, tracked_send)
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    body.extend(message.get("body", b""))
                    if len(body) > request_limit:
                        return await self.too_large(scope, receive, tracked_send)
                    if not message.get("more_body", False):
                        break

                async def replay():
                    return {"type": "http.request", "body": bytes(body), "more_body": False}

                await self.app(scope, replay, tracked_send)
            else:
                await self.app(scope, receive, tracked_send)
        except Exception:
            if response_started:
                raise
            await error_response(500, "internal_error", "The request could not be completed.")(
                scope,
                receive,
                tracked_send,
            )
        finally:
            route = scope.get("route")
            logger.info(
                json.dumps(
                    {
                        "request_id": request_id,
                        "method": scope["method"],
                        "route": getattr(route, "path", "unmatched"),
                        "status": status,
                        "duration_ms": round((time.monotonic() - started) * 1000, 2),
                    }
                )
            )

    async def too_large(self, scope, receive, send):
        await error_response(
            413,
            "payload_too_large",
            "Request body exceeds the allowed size.",
        )(scope, receive, send)


def create_app(host: str | None = None) -> FastAPI:
    validate_deployment_security(host)
    app = FastAPI(title="Resume Analysis API", version="1.0.0")
    app.state.rate_limiter = RequestRateLimiter(
        limit=int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "60")),
        window_seconds=60,
    )
    app.add_middleware(RequestBoundary, limiter=app.state.rate_limiter)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        if any(error["type"] == "json_invalid" for error in errors):
            return error_response(400, "invalid_json", "Request body must be valid JSON.")
        if any(error["type"] in {"model_attributes_type", "model_type"} for error in errors):
            return error_response(400, "invalid_request", "Request body must be a JSON object.")
        # Pydantic errors may include raw input and context: return neither.
        details = [
            {
                "field": ".".join(str(part) for part in error["loc"][1:]),
                "code": error["type"],
                "message": "This field is required." if error["type"] == "missing" else "Invalid field value.",
            }
            for error in errors
        ]
        return error_response(422, "validation_error", "Request validation failed.", details)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        codes = {404: "not_found", 405: "method_not_allowed", 400: "invalid_request", 415: "unsupported_media_type"}
        messages = {
            404: "Endpoint not found.",
            405: "Method not allowed.",
            400: "Request could not be parsed.",
            415: "Unsupported media type.",
        }
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        return error_response(
            exc.status_code,
            detail.get("code", codes.get(exc.status_code, "http_error")),
            detail.get("message", messages.get(exc.status_code, "Request rejected.")),
            headers=exc.headers,
        )

    app.include_router(router)
    return app


def resolve_server_config() -> tuple[str, int]:
    host = os.getenv("API_HOST", "127.0.0.1")
    try:
        port = int(os.getenv("PORT", "8001"))
    except ValueError as error:
        raise ValueError("PORT must be an integer.") from error
    return host, port


def run(host=None, port=None):
    configured_host, configured_port = resolve_server_config()
    effective_host = host or configured_host
    effective_port = port if port is not None else configured_port
    validate_deployment_security(effective_host)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    uvicorn.run(
        create_app(host=effective_host),
        host=effective_host,
        port=effective_port,
        access_log=False,
        proxy_headers=False,
    )


if __name__ == "__main__":
    run()
