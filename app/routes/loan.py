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

    if not all(
        k in data for k in ["project_type", "project_name", "address", "amount"]
    ):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        loan_service.create_loan(
            email=current_user["email"],
            project_type=data["project_type"],
            project_name=data["project_name"],
            address=data["address"],
            amount=data["amount"],
        )
        return jsonify({"status": "OK"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@loan_bp.route("/loans", methods=["GET"])
@jwt_required()
def get_loans():
    current_user = get_jwt()

    if "email" not in current_user.keys():
        return jsonify({"error": "Missing email in jwt"}), 400

    try:
        loans = loan_service.get_loans(email=current_user["email"])

        return (
            jsonify({"loans": [loan.to_dict() for loan in loans]}),
            201,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@loan_bp.route("/loan/<int:id>", methods=["GET"])
@jwt_required()
def get_loan(id):
    try:
        loan = loan_service.get_loan(id=id)
        return (
            jsonify({"loan": {**loan.to_dict(), "borrower": loan.user.to_dict()}}),
            201,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
