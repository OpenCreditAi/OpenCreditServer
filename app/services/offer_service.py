from typing import List

from flask import jsonify

from app import db
from app.models import Loan, Offer, User


class OfferService:
    def create_offer(
            self, offer_amount, interest_rate, offer_terms, repayment_period, loan_id, email
    ):

        user: User = User.query.filter_by(email=email).first()
        loan: Loan = Loan.query.filter_by(id=loan_id).first()

        if not user or not loan:
            raise ValueError("User or Loan does not exist")

        offer = Offer(
            user=user,
            loan=loan,
            organization=user.organization,
            offer_amount=offer_amount,
            interest_rate=interest_rate,
            offer_terms=offer_terms,
            repayment_period=repayment_period,
            status=Offer.Status.PENDING_BORROWER,
        )

        db.session.add(offer)
        db.session.commit()

        return offer

    def get_offers(self, loan_id):

        offers: List[Offer] = Offer.query.filter_by(loan_id=loan_id).all()

        return OfferService.__jsonify_offers(offers)

    def get_offers_organization(self, loan_id, email):

        organzation = db.session.query(User).filter_by(email=email).first().organization

        offers: List[Offer] = Offer.query.filter_by(loan_id=loan_id, organization_id=organzation.id).all()

        return OfferService.__jsonify_offers(offers)

    def accept(self, id):
        try:
            offer: Offer = Offer.query.get(id)
            offer.status = Offer.Status.ACCEPTED
            db.session.commit()
            return (
                jsonify(
                    {
                        "message": "Offer status updated successfully",
                        "offer_id": offer.id,
                        "new_status": offer.status,
                    }
                ),
                200,
            )
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    def reject(self, id):
        try:
            offer: Offer = Offer.query.get(id)
            offer.status = Offer.Status.REJECTED
            db.session.commit()
            return (
                jsonify(
                    {
                        "message": "Offer status updated successfully",
                        "offer_id": offer.id,
                        "new_status": offer.status,
                    }
                ),
                200,
            )
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def __jsonify_offers(offers: list):
        offer_list = []
        for offer in offers:
            offer_data = offer.to_dict()

            offer_list.append(offer_data)

        return jsonify(offer_list)
