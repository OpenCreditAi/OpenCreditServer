from app.routes.file import loan_service
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from app.models.user import User
from app.models.loan import Loan


chat_bp = Blueprint("chat", __name__)
chat_service = ChatService()
auth_service = AuthService()

@chat_bp.route("/chat/<int:loan_id>", methods=["GET"])
@jwt_required()
def get_chat(loan_id):
    current_user = get_jwt()
    loan: Loan = loan_service.get_loan(id=loan_id)

    if "email" not in current_user.keys():
        return jsonify({"error": "Missing required fields in jwt"}), 400

    user: User = User.query.filter_by(email=current_user["email"]).first()

    # Authorization check
    if (not any(offer.organization == user.organization for offer in loan.offers)) and user.id != loan.user_id:
        return jsonify({"error": "User unauthorized to view this chat"}), 403

    return chat_service.get_messages(loan_id)


@chat_bp.route("/chat/message/<int:loan_id>", methods=["POST"])
@jwt_required()
def new_message(loan_id):
    data = request.get_json()
    current_user = get_jwt()

    if "email" not in current_user:
        return jsonify({"error": "Missing required email in jwt"}), 400
    if "message" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    user: User = User.query.filter_by(email=current_user["email"]).first()

    loan: Loan = loan_service.get_loan(id=loan_id)

    if (not any(offer.organization == user.organization for offer in loan.offers)) and user.id != loan.user_id:
        return jsonify({"error": "User unauthorized to view this chat"}), 403

    chat_service.new_message(loan_id, current_user["email"], data["message"])
    return jsonify({"status": "OK"}), 200

