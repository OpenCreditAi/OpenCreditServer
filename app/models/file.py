from datetime import UTC, datetime  # Note: UTC is new in Python 3.11+

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class File(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loan.id"))
    file_name: Mapped[str]  # The document name, for example ״nosah_taboo.pdf״
    url: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))  # Updated to use UTC

    loan: Mapped["Loan"] = relationship("Loan", back_populates="files")
