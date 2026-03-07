import logging
import sys


class KeyValueFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        extra = {}
        for k in ("request_id", "method", "path", "status_code", "duration_ms", "user_id", "org_id"):
            if hasattr(record, k):
                extra[k] = getattr(record, k)

        merged = {**base, **extra}
        return " ".join([f"{k}={v}" for k, v in merged.items()])


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(KeyValueFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]

    logging.getLogger("uvicorn.access").handlers = [handler]