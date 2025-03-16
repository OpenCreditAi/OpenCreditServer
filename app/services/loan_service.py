from app import db
from app.models import Loan, User


class LoanService:
    def create_loan(self, email, project_name, adress):
        user = User.query.filter_by(email=email).first()
        loan = Loan(user=user, project_name=project_name, adress=adress)

        db.session.add(loan)
        db.session.commit()

        return loan
