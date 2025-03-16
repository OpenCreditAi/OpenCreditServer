from flask import Blueprint, jsonify, request

from app.services.loan_service import LoanService

loan_bp = Blueprint("loan", __name__)
loan_service = LoanService()


@loan_bp.route("/loan/create_loan", methods=["POST"])
def create_loan():
    data = request.get_json()

    if not all(k in data for k in ["email", "project_name", "adress"]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        loan_service.create_loan(email=data["email"], project_name=data["project_name"], adress=data["adress"])
        return jsonify({"status": "OK"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
