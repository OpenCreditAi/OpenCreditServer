import os
from datetime import datetime, UTC

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint

from app import db


class File(db.Model):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id", name="fk_file_loan"), nullable=False)
    file_name: Mapped[str] = mapped_column(nullable=False)  # Full filename, e.g., "document.pdf"
    file_basename: Mapped[str] = mapped_column(nullable=False)  # Filename without extension, e.g., "document"
    url: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    loan: Mapped["Loan"] = relationship("Loan", back_populates="files")

    __table_args__ = (
        UniqueConstraint("loan_id", "file_basename", name="uq_file_loan_basename"),  # Unique filenames per loan
        CheckConstraint("LENGTH(file_name) > 0", name="chk_file_name_not_empty"),
        CheckConstraint("LENGTH(file_basename) > 0", name="chk_file_basename_not_empty"),
    )

    def __init__(self, loan_id: int, file_name: str, url: str):
        self.loan_id = loan_id
        self.file_name = file_name
        self.file_basename = os.path.splitext(file_name)[0]  # Extract filename without extension
        self.url = url