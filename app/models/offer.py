from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class Offer(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    offer_amount: Mapped[int]
    interest_rate: Mapped[int]
    offerTerms: Mapped[str] 
    requestId: Mapped[int]
    status: Mapped[str]

    user: Mapped["User"] = relationship("User", back_populates="Offer")
