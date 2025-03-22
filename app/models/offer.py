from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class Offer(db.Model):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    offer_amount: Mapped[int]
    interest_rate: Mapped[int]
    offer_terms: Mapped[str]
    status: Mapped[str]
    repayment_period: Mapped[int]

    loan: Mapped["Loan"] = relationship("Loan", back_populates="offers")
    user: Mapped["User"] = relationship(
        "User"
    ) # No back_populates since user does not own offers - organization does
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="offers"
    )
