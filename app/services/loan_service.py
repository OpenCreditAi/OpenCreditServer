from app import db
from app.models import Loan, User


class LoanService:
    def create_loan(self, email, project_name, address, amount):
        user = User.query.filter_by(email=email).first()
        loan = Loan(user=user, project_name=project_name, address=address, amount=amount)

        db.session.add(loan)
        db.session.commit()

        return loan
