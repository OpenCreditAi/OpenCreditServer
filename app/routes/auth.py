from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.models.user import User
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not all(
        k in data
        for k in [
            "email",
            "password",
            "role",
            "fullName",
            "phoneNumber",
            "organizationName",
        ]
    ):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        user = auth_service.create_user(
            email=data["email"],
            password=data["password"],
            role=data["role"],
            full_name=data["fullName"],
            phone_number=data["phoneNumber"],
            organization_name=data["organizationName"],
        )
        aadditional_claims = {"id": user.id, "email": user.email, "role": user.role}
        access_token = create_access_token(identity=str(user.id), additional_claims=aadditional_claims)
        return jsonify({"access_token": access_token}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/auth/signin", methods=["POST"])
def signin():
    data = request.get_json()

    if not all(k in data for k in ["email", "password"]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        user: User = auth_service.authenticate_user(email=data["email"], password=data["password"])
        additional_claims = {"id": user.id, "email": user.email, "role": user.role}
        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
        return jsonify({"access_token": access_token})
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
