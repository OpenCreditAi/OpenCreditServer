from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from app.models import Loan
from app.services.loan_service import LoanService
from app.services.unified_email_service import UnifiedEmailService
from datetime import datetime, UTC

loan_bp = Blueprint("loan", __name__)
loan_service = LoanService()
email_service = UnifiedEmailService()


@loan_bp.route("/loans", methods=["POST"])
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
        loan: Loan = loan_service.create_loan(
            email=current_user["email"],
            project_type=data["project_type"],
            project_name=data["project_name"],
            address=data["address"],
            amount=data["amount"],
        )
        return jsonify({"id": loan.id}), 201
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
            200,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@loan_bp.route("/loans/marketplace", methods=["GET"])
@jwt_required()
def get_marketplace_loans():
    current_user = get_jwt()

    if "email" not in current_user.keys():
        return jsonify({"error": "Missing email in jwt"}), 400

    try:
        loans = loan_service.get_marketplace_loans(email=current_user["email"])

        return (
            jsonify({"loans": [loan.to_dict() for loan in loans]}),
            200,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@loan_bp.route("/loans/<int:id>", methods=["GET"])
@jwt_required()
def get_loan(id):
    try:
        loan = loan_service.get_loan(id=id)
        return (
            jsonify({"loan": {**loan.to_dict(), "borrower": loan.user.to_dict()}}),
            200,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@loan_bp.route("/loans/<int:id>/status", methods=["PUT"])
@jwt_required()
def update_loan_status(id):
    """
    Update loan status and send email notification
    """
    data = request.get_json()
    current_user = get_jwt()
    
    if "email" not in current_user.keys():
        return jsonify({"error": "Missing email in jwt"}), 400
    
    if "status" not in data:
        return jsonify({"error": "Missing status field"}), 400
    
    try:
        # Get the loan
        loan = loan_service.get_loan(id=id)
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
        
        # Check if user has permission to update this loan
        user_email = current_user["email"]
        if loan.user.email != user_email and loan.organization.users.filter_by(email=user_email).first() is None:
            return jsonify({"error": "Unauthorized to update this loan"}), 403
        
        # Validate status
        try:
            new_status = Loan.Status(data["status"])
        except ValueError:
            valid_statuses = [status.name for status in Loan.Status]
            return jsonify({"error": f"Invalid status. Valid statuses: {valid_statuses}"}), 400
        
        # Store old status for email notification
        old_status = loan.status.name if loan.status else None
        
        # Update loan status
        loan_service.update_loan_status(id, new_status)
        
        # Prepare loan data for email
        loan_data = {
            "project_name": loan.project_name,
            "amount": loan.amount,
            "borrower_name": loan.user.name,
            "borrower_email": loan.user.email,
            "updated_at": datetime.now(UTC).strftime("%d/%m/%Y %H:%M")
        }
        
        # Send email notification
        try:
            email_sent = email_service.send_loan_status_notification(
                loan_data, old_status, new_status.name
            )
            if email_sent:
                print(f"Email notification sent for loan {id} status change: {old_status} -> {new_status.name}")
            else:
                print(f"Failed to send email notification for loan {id}")
        except Exception as e:
            print(f"Error sending email notification for loan {id}: {str(e)}")
            # Don't fail the request if email fails
        
        return jsonify({
            "message": "Loan status updated successfully",
            "loan_id": id,
            "old_status": old_status,
            "new_status": new_status.name,
            "email_sent": email_sent if 'email_sent' in locals() else False
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
