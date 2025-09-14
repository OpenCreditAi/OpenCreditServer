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
        # Check if user is the borrower or a member of the organization
        is_authorized = (loan.user.email == user_email or 
                        any(user.email == user_email for user in loan.organization.users))
        if not is_authorized:
            return jsonify({"error": "Unauthorized to update this loan"}), 403
        
        # Validate status - handle both string names and numeric values
        try:
            status_value = data["status"]
            
            # If it's a string, try to find by name
            if isinstance(status_value, str):
                new_status = Loan.Status[status_value]
            # If it's a number, try to find by value
            elif isinstance(status_value, (int, float)):
                new_status = Loan.Status(int(status_value))
            else:
                raise ValueError("Status must be string or number")
                
        except (ValueError, KeyError):
            valid_statuses = [status.name for status in Loan.Status]
            return jsonify({"error": f"Invalid status. Valid statuses: {valid_statuses}"}), 400
        
        # Store old status for email notification
        old_status = loan.status.name if loan.status else None
        
        # Update loan status
        loan_service.update_loan_status(id, new_status)
        
        # Prepare loan data for email
        # Get financier email from organization users (first user with financier role)
        financier_email = None
        financier_name = loan.organization.name
        
        # Try to find a financier user in the organization
        for user in loan.organization.users:
            if hasattr(user, 'role') and user.role == 'financier':
                financier_email = user.email
                financier_name = user.full_name
                break
        
        # If no financier found, use the first user's email or a default
        if not financier_email and loan.organization.users:
            financier_email = loan.organization.users[0].email
            financier_name = loan.organization.users[0].full_name
        
        loan_data = {
            "project_name": loan.project_name,
            "amount": loan.amount,
            "borrower_name": loan.user.full_name,
            "borrower_email": loan.user.email,
            "financier_name": financier_name,
            "financier_email": financier_email,
            "updated_at": datetime.now(UTC).strftime("%d/%m/%Y %H:%M")
        }
        
        # Send email notifications to both parties
        borrower_email_sent = False
        financier_email_sent = False
        
        # Send email to borrower
        if loan_data.get('borrower_email'):
            try:
                borrower_email_sent = email_service.send_loan_status_notification(
                    loan_data, old_status, new_status.name, recipient_type="borrower"
                )
                if borrower_email_sent:
                    print(f"Email notification sent to borrower for loan {id} status change: {old_status} -> {new_status.name}")
                else:
                    print(f"Failed to send email notification to borrower for loan {id}")
            except Exception as e:
                print(f"Error sending email notification to borrower for loan {id}: {str(e)}")
                borrower_email_sent = False
        else:
            print(f"No borrower email found for loan {id}")
            borrower_email_sent = False
        
        # Send email to financier
        if loan_data.get('financier_email'):
            try:
                financier_email_sent = email_service.send_loan_status_notification(
                    loan_data, old_status, new_status.name, recipient_type="financier"
                )
                if financier_email_sent:
                    print(f"Email notification sent to financier for loan {id} status change: {old_status} -> {new_status.name}")
                else:
                    print(f"Failed to send email notification to financier for loan {id}")
            except Exception as e:
                print(f"Error sending email notification to financier for loan {id}: {str(e)}")
                financier_email_sent = False
        else:
            print(f"No financier email found for loan {id}")
            financier_email_sent = False
        
        return jsonify({
            "message": "Loan status updated successfully",
            "loan_id": id,
            "old_status": old_status,
            "new_status": new_status.name,
            "borrower_email_sent": borrower_email_sent,
            "financier_email_sent": financier_email_sent,
            "emails_sent": borrower_email_sent or financier_email_sent
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
