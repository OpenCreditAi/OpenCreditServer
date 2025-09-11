from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db
from enum import IntEnum
from sqlalchemy import Enum as SqlEnum

from app.models.loan import Loan


class Offer(db.Model):
    class Status(IntEnum):
        PENDING_FINANCIER = 0
        PENDING_BORROWER = 1
        EXPIRED = 2
        ACCEPTED = 3
        REJECTED = 4

        def closed(self):
            return self in [self.ACCEPTED, self.REJECTED, self.EXPIRED]

    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    offer_amount: Mapped[int]
    interest_rate: Mapped[int]
    offer_terms: Mapped[str]
    status = db.Column(SqlEnum(Status, name="status_enum", native_enum=False), nullable=False)
    repayment_period: Mapped[int]

    loan: Mapped["Loan"] = relationship("Loan", back_populates="offers")
    user: Mapped["User"] = relationship("User")  # No back_populates since user does not own offers - organization does
    organization: Mapped["Organization"] = relationship("Organization", back_populates="offers")

    def to_dict(self):
        return {
            "id": self.id,
            "loan_id": self.loan_id,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "organization_name": self.organization.name,
            "offer_amount": self.offer_amount,
            "interest_rate": self.interest_rate,
            "offer_terms": self.offer_terms,
            "status": self.status.name,
            "repayment_period": self.repayment_period,
        }
