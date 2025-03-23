from app import db
from app.models import Loan, User, Organization


class OrganizationService:
    def get_organization(self, organization_name):
        organization = Organization.query.filter_by(
            name=organization_name
        ).first()

        if not organization:
            organization = Organization(name=organization_name)
            db.session.add(organization)
            db.session.commit()

        return organization
