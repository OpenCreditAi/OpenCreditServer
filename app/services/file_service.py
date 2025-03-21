import os

from werkzeug.datastructures import FileStorage

from app import db
from app.config import Config
from app.models import File, Loan


class FileService:
    def upload_file(self, loan_id: int, file_name: str, file: FileStorage):
        loan: Loan = Loan.query.filter_by(id=loan_id).first()
        if not loan:
            raise ValueError(f"No such loan with id ${loan_id}")

        loan_dir_path = os.path.join(Config.UPLOAD_FOLDER, str(loan_id))
        os.makedirs(loan_dir_path, exist_ok=True)
        file_path = os.path.join(loan_dir_path, file_name)
        file.save(file_path)

        file_model = File(loan_id=loan.id, file_name=file_name, url=file_path)

        db.session.add(file_model)
        db.session.commit()

        return file

    def get_file_url(self, loan_id: int, file_name: str):
        file: File = File.query.filter_by(loan_id=loan_id, file_basename=os.path.splitext(file_name)[0]).first()

        if not file:
            raise ValueError(f"No such file as {file_name} for loan {loan_id}")

        return file.url
