from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from app.services.loan_service import LoanService

loan_bp = Blueprint("loan", __name__)
loan_service = LoanService()


@loan_bp.route("/loan/create_loan", methods=["POST"])
@jwt_required()
def create_loan():
    data = request.get_json()
    current_user = get_jwt()

    if "email" not in current_user.keys():
        return jsonify({"error": "Missing email in jwt"}), 400

    if not all(k in data for k in ["project_name", "adress", "amount"]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        loan_service.create_loan(email=current_user["email"], project_name=data["project_name"], adress=data["adress"], amount=data["amount"])
        return jsonify({"status": "OK"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
