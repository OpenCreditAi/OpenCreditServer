import os

from werkzeug.datastructures import FileStorage

from app import db
from app.config import Config
from app.models import File, Loan


class FileService:
    def upload_file(self, loan_id: int, file_name: str, file: FileStorage):
        loan: Loan = Loan.query.filter_by(id=loan_id).first()
        if not loan:
            raise ValueError(f"No such loan with id {loan_id}")

        # Ensure loan directory exists
        loan_dir_path = os.path.join(Config.UPLOAD_FOLDER, str(loan_id))
        os.makedirs(loan_dir_path, exist_ok=True)

        # Extract basename (without extension) for uniqueness
        base_name, ext = os.path.splitext(file_name)

        # Look for existing file with same basename
        existing_file = (
            File.query
            .filter_by(loan_id=loan.id)
            .filter(File.file_name.like(f"{base_name}.%"))
            .first()
        )

        # If there’s an existing file, remove it from disk + update record
        if existing_file:
            try:
                if os.path.exists(existing_file.url):
                    os.remove(existing_file.url)  # delete old file
            except Exception as e:
                # Log the error instead of failing silently
                print(f"Warning: could not remove old file {existing_file.url}: {e}")

            # Save new file in the same loan folder
            file_path = os.path.join(loan_dir_path, file_name)
            file.save(file_path)

            # Update existing DB record
            existing_file.file_name = file_name
            existing_file.url = file_path

        else:
            # Save new file normally
            file_path = os.path.join(loan_dir_path, file_name)
            file.save(file_path)

            # Create DB record
            file_model = File(loan_id=loan.id, file_name=file_name, url=file_path)
            db.session.add(file_model)

        db.session.commit()

    def get_file_url(self, loan_id: str, file_basename: str):
        file: File = File.query.filter_by(loan_id=loan_id, file_basename=file_basename).first()

        if not file:
            raise ValueError(f"No such file as {file_basename} for loan {loan_id}")

        return file.url
