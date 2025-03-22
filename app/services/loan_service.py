from app import db
from app.models import Loan, User


class LoanService:
    def create_loan(self, email, project_type, project_name, address, amount):
        user = User.query.filter_by(email=email).first()
        loan = Loan(
            user=user,
            project_type=project_type,
            project_name=project_name,
            address=address,
            amount=amount,
        )

        db.session.add(loan)
        db.session.commit()

        return loan

    def get_loans(self, email):
        user = User.query.filter_by(email=email).first()

        if user.role == "financier":
            return Loan.query.all()
        else:
            return Loan.query.filter_by(user_id=user.id).all()

    def get_loan(self, id):
        return Loan.query.get(id)
