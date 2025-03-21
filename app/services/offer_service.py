from typing import List

from flask import jsonify

from app import db
from app.models import Loan, Offer, User


class OfferService:
    def create_offer(self, offer_amount, interest_rate, offer_terms, repayment_period, loan_id, email):

        user: User = User.query.filter_by(email=email).first()
        loan: Loan = Loan.query.filter_by(id=loan_id).first()

        if not user or not loan:
            raise ValueError("User or Loan does not exist")

        offer = Offer(
            user=user,
            loan=loan,
            offer_amount=offer_amount,
            interest_rate=interest_rate,
            offer_terms=offer_terms,
            repayment_period=repayment_period,
            status="Pending",
        )

        db.session.add(offer)
        db.session.commit()

        return offer

    def get_offers(self, loan_id):

        offers: List[Offer] = Offer.query.filter_by(loan_id=loan_id).all()
        offer_list = []

        for offer in offers:
            offer_data = {
                "offer_amount": offer.offer_amount,
                "interest_rate": offer.interest_rate,
                "repayment_period": offer.repayment_period,
                "status": offer.status,
                "id": offer.id,
                "user_name": offer.user.email, #until there is organization that the user is related to
            }
            offer_list.append(offer_data)

        return jsonify(offer_list)

    def accept(self, id):
        try:
            offer: Offer = Offer.query.get(id)
            offer.status = "Accepted"
            db.session.commit()
            return jsonify({"message": "Offer status updated successfully", "offer_id": offer.id, "new_status": offer.status}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    def reject(self, id):
        try:
            offer: Offer = Offer.query.get(id)
            offer.status = "Denied"
            db.session.commit()
            return jsonify({"message": "Offer status updated successfully", "offer_id": offer.id, "new_status": offer.status}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
