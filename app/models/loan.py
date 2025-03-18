from datetime import UTC, datetime  # Note: UTC is new in Python 3.11+
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class Loan(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    project_name: Mapped[str]
    adress: Mapped[str]
    amount: Mapped[int]  # Amount of money needed
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))  # Updated to use UTC

    user: Mapped["User"] = relationship("User", back_populates="loans")
    files: Mapped[List["File"]] = relationship("File", back_populates="loan")
