from flask import Blueprint, jsonify, request

from app.services.offer_service import OfferService

offer_bp = Blueprint("offer", __name__)
offer_service = OfferService()


@offer_bp.route("/offer/new", methods=["POST"])
def new_request():
    data = request.get_json()

    if not all(k in data for k in ["offerAmount", "interestRate", "offerTerms", "requestId"]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        user = offer_service.create_offer(offerAmount=data["offerAmount"], interestRate=data["interestRate"],
 offerTerms=data["offerTerms"], requestId=data["requestId"] )
        return 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
