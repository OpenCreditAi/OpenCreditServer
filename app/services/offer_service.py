from app import db
from app.models import Offer, User


class OfferService:
    def create_offer(self, offerAmount, interestRate, offerTerms, requestId):
        user = User.query.filter_by(email=email).first()
        offer = Loan(user=user, offerAmount=offerAmount, interestRate=interestRate, offerTerms=offerTerms, requestId=requestId)

        db.session.add(offer)
        db.session.commit()

        return offer


    def get_offers(self, requestId):
        offer = Offer.query.filter_by(requestId=requestId).first()

        if not offer:
            raise ValueError("Invalid requestId")

        return offer
