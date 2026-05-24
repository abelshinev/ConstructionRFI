from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from storage.database.connect import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    sha256: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    stored_path: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    processing_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="uploaded",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )