from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.services.file_service import FileService

file_bp = Blueprint("file", __name__)
file_service = FileService()


@file_bp.route("/file/upload_files", methods=["POST"])
def upload_files():
    data = request.form
    files = request.files
    file_names = files.keys()

    if len(files) <= 0:
        return jsonify({"error": "Missing Files"}), 400

    if not all(k in data for k in ["loan_id"]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        for file in file_names:
            file_service.upload_file(data["loan_id"], secure_filename(files[file].filename), files[file])

        return jsonify({"status": "OK"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
