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
            status=Loan.Status.MISSING_DOCUMENTS,
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

    def update_loan_status(self, loan_id, status):
        loan: Loan = Loan.query.filter_by(id=loan_id).first()

        if not loan:
            raise ValueError(f"No such loan with id ${loan_id}")

        loan.status = status
        db.session.commit()

    def _essential_files_exists(self, files: list):
        essential_files = ["tabo_document",
                           "united_home_document",
                           "original_tama_document",
                           "project_list_document",
                           "company_crt_document",
                           "tama_addons_document",
                           "reject_status_document",
                           "building_permit",
                           "objection_status",
                           "zero_document",
                           "bank_account_confirm_document"]
        file_names = [file.file_basename for file in files]


        for essential in essential_files:
            if not (essential in file_names):
                return False
        return True

    def essential_files_exists(self, loan: Loan):
        return self._essential_files_exists(loan.files)
