from flask import Blueprint, jsonify, request
from jwt import decode
from app.config import Config


from app.services.offer_service import OfferService

offer_bp = Blueprint("offer", __name__)
offer_service = OfferService()


@offer_bp.route("/offer/new", methods=["POST"])
def new_request():
    data = request.get_json()

    if not all(k in data for k in ["offerAmount", "interestRate", "offerTerms", "repaymentPeriod", "requestId", "token"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    
    jwt_secret_key = Config.JWT_SECRET_KEY
    token_data = decode(data["token"], jwt_secret_key, algorithms=["HS256"])
    print("Decoded Token:", token_data)
    
    
    try:
        offer_service.create_offer(offerAmount=data["offerAmount"], interestRate=data["interestRate"],
 offerTerms=data["offerTerms"], repaymentPeriod=data["repaymentPeriod"], requestId=data["requestId"], email=token_data["email"])
        return jsonify({"status": "OK"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@offer_bp.route("/offer/get/<int:id>", methods=["GET"])
def get_offer(id):
    
    try:
        offers = offer_service.get_offers(requestId=id)
        return offers
    except ValueError as e:
        return jsonify({})
    

@offer_bp.route("/offer/accept/<string:id>", methods=["PATCH"])
def accept_offer(id):
    try:
        offer_service.accept(id=id)
        return jsonify({"status": "OK"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@offer_bp.route("/offer/reject/<string:id>", methods=["PATCH"])
def reject_offer(id):
    try:
        offer_service.reject(id=id)
        return jsonify({"status": "OK"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
