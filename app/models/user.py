from datetime import UTC, datetime  # Note: UTC is new in Python 3.11+
from typing import List

import bcrypt
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[bytes] = mapped_column()
    role: Mapped[str] = mapped_column(String(30))  # 'borrower' or 'financier'
    full_name: Mapped[str]
    phone_number: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC)
    )  # Updated to use UTC

    loans: Mapped[List["Loan"]] = relationship("Loan", back_populates="user")
    offers: Mapped[List["Offer"]] = relationship("Offer", back_populates="user")

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
        }
