import pytest
from app.services.auth_service import AuthService
from app.models.user import User
from app import db

def test_create_user(app):
    with app.app_context():
        auth_service = AuthService()
        
        user = auth_service.create_user(
            email='new@example.com',
            password='secret123',
            role='financier'
        )
        
        assert user.id is not None
        assert user.email == 'new@example.com'
        assert user.role == 'financier'
        assert user.check_password('secret123') is True
        
        # Check it's in the database
        saved_user = User.query.filter_by(email='new@example.com').first()
        assert saved_user is not None

def test_create_duplicate_user(app, test_user):
    with app.app_context():
        auth_service = AuthService()
        
        # Should raise error for duplicate email
        with pytest.raises(ValueError) as excinfo:
            auth_service.create_user(
                email='test@example.com',  # Same as test_user
                password='new_password',
                role='borrower'
            )
            
        assert 'Email already registered' in str(excinfo.value)

def test_authenticate_user(app):
    with app.app_context():
        # Create a user specifically for this test
        auth_service = AuthService()
        auth_service.create_user(
            email='auth_test@example.com',
            password='password123',
            role='borrower'
        )
        
        # Valid credentials
        user = auth_service.authenticate_user('auth_test@example.com', 'password123')
        assert user is not None
        assert user.email == 'auth_test@example.com'
        
        # Invalid email
        with pytest.raises(ValueError):
            auth_service.authenticate_user('wrong@example.com', 'password123')
            
        # Invalid password
        with pytest.raises(ValueError):
            auth_service.authenticate_user('auth_test@example.com', 'wrongpassword')
