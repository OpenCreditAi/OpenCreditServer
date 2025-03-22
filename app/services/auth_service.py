from app import db
from app.models import User


class AuthService:
    def create_user(self, email, password, role, full_name, phone_number, organization) -> User:
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already registered")

        user = User(email=email, role=role, full_name=full_name, phone_number=phone_number, organization=organization)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user

    def authenticate_user(self, email, password) -> User:
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            raise ValueError("Invalid email or password")

        return user
