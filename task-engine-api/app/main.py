from fastapi import FastAPI , Request
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.api.health import router as health_router
from app.api.orgs import router as orgs_router
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.me import router as me_router
import traceback
from fastapi.responses import PlainTextResponse , JSONResponse
from sqlalchemy.exc import IntegrityError
from app.core.errors import ApiErrorResponse


app = FastAPI(title=settings.app_name)



@app.exception_handler(Exception)
async def debug_exception_handler(request, exc: Exception):
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

    # FastAPI'nin HTTPBearer şemasına uyumlu isim: "HTTPBearer"
    openapi_schema.setdefault("components", {})
    openapi_schema["components"].setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["HTTPBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    # Swagger'ın token'ı request'lere eklemesi için global security requirement
    openapi_schema["security"] = [{"HTTPBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    # Session failed state -> rollback şart.
    db = request.state.db if hasattr(request.state, "db") else None
    if db:
        db.rollback()

    pgcode = getattr(getattr(exc, "orig", None), "pgcode", None)

    if pgcode == "23505":
       constraint = getattr(getattr(getattr(exc, "orig", None), "diag", None), "constraint_name", None)
       
       if constraint == "uq_users_org_id_email":
           return JSONResponse(
               status_code=409,
               content=ApiErrorResponse(
                   error={"code": "EMAIL_ALREADY_EXISTS", "message": "Email already exists in this organization"}
               ).model_dump(), 
           
           )
           
       return JSONResponse(
           status_code=409,
              content=ApiErrorResponse(
                error={"code": "EMAIL_ALREADY_EXISTS", "message": "Duplicate value violates unique constraint"}
              ).model_dump(),
         ) 


app.openapi = custom_openapi


app.include_router(health_router)
app.include_router(orgs_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(me_router)