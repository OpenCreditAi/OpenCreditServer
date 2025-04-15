from app import db
from app.models import Loan, User


class LoanService:
    def create_loan(self, email, project_type, project_name, address, amount):
        user = User.query.filter_by(email=email).first()
        loan = Loan(
            user=user,
            organization=user.organization,
            project_type=project_type,
            project_name=project_name,
            address=address,
            amount=amount,
            status=Loan.Status.PROCESSING_DOCUMENTS,
        )

        db.session.add(loan)
        db.session.commit()

        return loan

    def get_loans(self, email):
        user = User.query.filter_by(email=email).first()

        if user.role == "financier":
            return set([offer.loan for offer in user.organization.offers])
        else:
            return Loan.query.filter_by(organization_id=user.organization_id)

    def get_marketplace_loans(self):
        return Loan.query.all()

    def get_loan(self, id):
        return Loan.query.get(id)
