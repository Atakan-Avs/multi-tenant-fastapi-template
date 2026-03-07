from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.mixins import AuditMixin

class Organization(AuditMixin, Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)