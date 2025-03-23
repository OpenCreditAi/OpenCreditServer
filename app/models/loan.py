from datetime import UTC, datetime  # Note: UTC is new in Python 3.11+
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class Loan(db.Model):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    project_type: Mapped[str]
    project_name: Mapped[str]
    address: Mapped[str]
    amount: Mapped[int]  # Amount of money needed
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC)
    )  # Updated to use UTC

    user: Mapped["User"] = relationship(
        "User"
    )  # No back_populates since user does not own offers - organization does
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="loans"
    )
    files: Mapped[List["File"]] = relationship("File", back_populates="loan")
    offers: Mapped[List["Offer"]] = relationship("Offer", back_populates="loan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_type": self.project_type,
            "project_name": self.project_name,
            "address": self.address,
            "amount": self.amount,
            "created_at": self.created_at,
            "organization_name": self.organization.name,
            "file_names": [file.name for file in self.files]
        }
