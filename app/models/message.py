from datetime import datetime, UTC
from typing import List
from unittest.mock import sentinel

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class Message(db.Model):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str]
    sent_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    loan: Mapped[List["Loan"]] = relationship("Loan", back_populates="chat")
    sender: Mapped["User"] = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "loan_id": self.loan_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender.full_name,
            "sender_role": self.sender.role,
            "message": self.message,
            "sent_at": self.sent_at.isoformat()
        }
