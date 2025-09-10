from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from app.models import Loan
from app.services.document_analysis.validate_file import validate_file
from app.services.file_service import FileService
from app.services.loan_service import LoanService

file_bp = Blueprint("file", __name__)
file_service = FileService()
loan_service = LoanService()

@file_bp.route("/file/upload_files", methods=["POST"])
@jwt_required()
def upload_files():
    data = request.form
    files = request.files.getlist("files")

    if len(files) <= 0:
        return jsonify({"error": "Missing Files"}), 400

    if not all(k in data for k in ["loan_id"]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        loan = loan_service.get_loan(id=data["loan_id"])

        unaccepted_files = []

        for file in files:
            if not validate_file(file):
                unaccepted_files.append(file.filename)
                continue

            # Save only if validation passed
            file_service.upload_file(loan.id, secure_filename(file.filename), file)

        # If any failed validation → return error with list
        if unaccepted_files:
            return jsonify({
                "error": f"error code 415: the following files are not following our guidelines: {unaccepted_files}",
                "unaccepted_files": unaccepted_files
            }), 415

        # If all passed → proceed
        if loan_service.essential_files_exists(loan) and loan.status == Loan.Status.MISSING_DOCUMENTS:
            loan_service.update_loan_status(data["loan_id"], Loan.Status.WAITING_FOR_OFFERS)

        return jsonify({"status": "OK"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@file_bp.route("/file/download_file", methods=["GET"])
@jwt_required()
def download_file():
    loan_id = request.args.get("loan_id")
    file_basename = request.args.get("file_basename")

    if not loan_id or not file_basename:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        file = file_service.get_file_url(loan_id, secure_filename(file_basename))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return send_file(file)

