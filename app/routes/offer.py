from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from app.services.offer_service import OfferService

offer_bp = Blueprint("offer", __name__)
offer_service = OfferService()


@offer_bp.route("/offer/new", methods=["POST"])
@jwt_required()
def new_request():
    data = request.get_json()
    current_user = get_jwt()

    if "email" not in current_user.keys():
        return jsonify({"error": "Missing email in jwt"}), 400

    if not all(k in data for k in ["offer_amount", "interest_rate", "offer_terms", "repayment_period", "loan_id"]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        offer_service.create_offer(
            offer_amount=data["offer_amount"],
            interest_rate=data["interest_rate"],
            offer_terms=data["offer_terms"],
            repayment_period=data["repayment_period"],
            loan_id=data["loan_id"],
            email=current_user["email"],
        )
        return jsonify({"status": "OK"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@offer_bp.route("/offer/get/<int:id>", methods=["GET"])
@jwt_required()
def get_offer(id):
    try:
        offers = offer_service.get_offers(loan_id=id)
        return offers
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@offer_bp.route("/offer/get/org/<int:id>", methods=["GET"])
@jwt_required()
def get_org_offer(id):
    try: 
        current_user = get_jwt()
        offers = offer_service.get_offers_organization(loan_id=id, email=current_user['email'])
        
        return offers
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@offer_bp.route("/offer/accept/<int:id>", methods=["PATCH"])
@jwt_required()
def accept_offer(id):
    try:
        offer_service.accept(id=id)
        return jsonify({"status": "OK"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@offer_bp.route("/offer/reject/<int:id>", methods=["PATCH"])
@jwt_required()
def reject_offer(id):
    try:
        offer_service.reject(id=id)
        return jsonify({"status": "OK"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
