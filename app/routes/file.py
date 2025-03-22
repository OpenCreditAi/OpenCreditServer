from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt, jwt_required
from werkzeug.utils import secure_filename

from app.services.file_service import FileService

file_bp = Blueprint("file", __name__)
file_service = FileService()


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
        for file in files:
            file_service.upload_file(data["loan_id"], secure_filename(file.filename), file)

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

