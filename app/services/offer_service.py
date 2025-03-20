from app import db
from app.models import Offer, User
from flask import jsonify



class OfferService:
    def create_offer(self, offerAmount, interestRate, offerTerms, repaymentPeriod, requestId, email):
                        
        user = User.query.filter_by(email=email).first()
        offer = Offer(user=user, offer_amount=offerAmount, interest_rate=interestRate, offer_terms=offerTerms,
                      repayment_period=repaymentPeriod, request_id=int(requestId), status="Pending")
        
        db.session.add(offer)
        db.session.commit()
        
        return offer


    def get_offers(self, requestId):
        
        offers = Offer.query.filter_by(request_id=requestId).all()
        
        offer_list = []
        
        for offer in offers:
          offer_data = {
            "offer_amount": offer.offer_amount,
            "interest_rate": offer.interest_rate,
            "repayment_period": offer.repayment_period,
            "user_name": offer.user.email, 
            "status": offer.status,
            "id": offer.id
          }
          offer_list.append(offer_data)
        
        
        return jsonify(offer_list)
    
    def accept(self, id):
        try:
            offer = Offer.query.get(id)
            offer.status = "Accepted"
            db.session.commit()
            return jsonify({"message": "Offer status updated successfully", "offer_id": offer.id, "new_status": offer.status}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    def reject(self, id):
        try:
            offer = Offer.query.get(id)
            offer.status = "Denied"
            db.session.commit()
            return jsonify({"message": "Offer status updated successfully", "offer_id": offer.id, "new_status": offer.status}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500



