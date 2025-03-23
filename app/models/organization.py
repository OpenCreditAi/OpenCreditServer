from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class Organization(db.Model):
    __tablename__ = 'organizations'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    users: Mapped[List["User"]] = relationship("User", back_populates="organization")
    loans: Mapped[List["Loan"]] = relationship("Loan", back_populates="organization")
    offers: Mapped[List["Offer"]] = relationship("Offer", back_populates="organization")
