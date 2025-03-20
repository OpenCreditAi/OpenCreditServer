from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class Offer(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    loan_id: Mapped[int] = mapped_column(ForeignKey("loan.id"))
    offer_amount: Mapped[int]
    interest_rate: Mapped[int]
    offer_terms: Mapped[str]
    status: Mapped[str]
    repayment_period: Mapped[int]

    user: Mapped["User"] = relationship("User", back_populates="offers")
    loan: Mapped["Loan"] = relationship("Loan", back_populates="offers")
