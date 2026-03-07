import time
import uuid
import logging

from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.models import User
from app.db.session import SessionLocal

logger = logging.getLogger("app")


def _extract_user_id_from_bearer(request: Request) -> int | None:
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        return None

    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        sub = payload.get("sub")
        if not sub:
            return None
        return int(sub)
    except (JWTError, ValueError):
        return None


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        user_id = _extract_user_id_from_bearer(request)
        request.state.user_id = user_id

        # --- client context (ip + user agent)
        user_agent = request.headers.get("user-agent") or request.headers.get("User-Agent")
        request.state.user_agent = user_agent

        xff = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For")
        if xff:
            client_ip = xff.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else None
        request.state.client_ip = client_ip

        # --- org_id lookup (DB) - güvenli / non-blocking yaklaşım
        # Health gibi endpointlerde DB'ye hiç dokunma (sonsuz bekleme riskini sıfırlar)
        org_id = None
        if request.url.path != "/health" and user_id is not None:
            db = SessionLocal()
            try:
                user = db.get(User, user_id)
                if user and getattr(user, "deleted_at", None) is None:
                    org_id = user.org_id
            except Exception:
                # DB problem olsa bile request'i kilitlemeyelim
                logger.exception(
                    "org_lookup_failed",
                    extra={
                        "request_id": request_id,
                        "user_id": user_id,
                        "path": request.url.path,
                    },
                )
                org_id = None
            finally:
                db.close()

        request.state.org_id = org_id

        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "org_id": org_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-Id"] = request_id

        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "org_id": org_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response