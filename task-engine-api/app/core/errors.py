from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    rid = get_request_id(request)
    payload = {"detail": exc.detail}
    if rid:
        payload["request_id"] = rid
    return JSONResponse(status_code=exc.status_code, content=payload)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    rid = get_request_id(request)
    payload = {"detail": exc.errors()}
    if rid:
        payload["request_id"] = rid
    return JSONResponse(status_code=422, content=payload)