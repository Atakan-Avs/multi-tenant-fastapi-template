from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError
import traceback

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware

from app.api.health import router as health_router
from app.api.orgs import router as orgs_router
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.me import router as me_router
from app.api.auth_refresh import router as auth_refresh_router
from app.api.auth_logout import router as auth_logout_router
from app.api.task import router as tasks_router
from app.api.auth_sessions import router as auth_sessions_router
from app.api.rbac_admin import router as rbac_admin_router


app = FastAPI(title=settings.app_name)
setup_logging()
app.add_middleware(RequestContextMiddleware)


def _error_payload(request: Request, code: str, message: str):
    request_id = getattr(request.state, "request_id", None)
    return {
        "error": {"code": code, "message": message},
        "request_id": request_id,
    }


@app.exception_handler(HTTPException)
async def http_exception_handler_local(request: Request, exc: HTTPException):
    code_map = {
        400: "bad_request",
        401: "not_authenticated",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
    }
    code = code_map.get(exc.status_code, "http_error")

    # exc.detail bazen str bazen dict olabilir, stringleştiriyoruz
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(request, code=code, message=message),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler_local(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=_error_payload(request, code="validation_error", message="Invalid request body"),
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    # Session failed state -> rollback şart.
    db = getattr(request.state, "db", None)
    if db:
        db.rollback()

    pgcode = getattr(getattr(exc, "orig", None), "pgcode", None)

    if pgcode == "23505":
        constraint = getattr(getattr(getattr(exc, "orig", None), "diag", None), "constraint_name", None)

        if constraint == "uq_users_org_id_email":
            return JSONResponse(
                status_code=409,
                content=_error_payload(
                    request,
                    code="EMAIL_ALREADY_EXISTS",
                    message="Email already exists in this organization",
                ),
            )

        return JSONResponse(
            status_code=409,
            content=_error_payload(
                request,
                code="DUPLICATE_VALUE",
                message="Duplicate value violates unique constraint",
            ),
        )

    # Diğer integrity error'lar
    return JSONResponse(
        status_code=409,
        content=_error_payload(request, code="integrity_error", message="Integrity error"),
    )


@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    return PlainTextResponse(traceback.format_exc(), status_code=500)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="TaskEngine API",
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {})
    openapi_schema["components"].setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["HTTPBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    openapi_schema["security"] = [{"HTTPBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# routers
app.include_router(health_router)
app.include_router(orgs_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(me_router)
app.include_router(auth_refresh_router)
app.include_router(auth_logout_router)
app.include_router(tasks_router)
app.include_router(auth_sessions_router)
app.include_router(rbac_admin_router)


# Starlette HTTPException'ı da yakalansın
app.add_exception_handler(StarletteHTTPException, http_exception_handler_local)