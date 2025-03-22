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
            role='financier',
            full_name='New User',
            phone_number='1234567890',
            organization='New Organization'
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
                email='test@example.com',  # Use the same email as test_user
                password='new_password',
                role='borrower',
                full_name='Test User',
                phone_number='1234567890',
                organization='Test Organization'
            )
            
        assert 'Email already registered' in str(excinfo.value)

def test_authenticate_user(app):
    with app.app_context():
        auth_service = AuthService()
        auth_service.create_user(
            email='auth_test@example.com',
            password='password123',
            role='borrower',
            full_name='Auth Test',
            phone_number='1234567890',
            organization='Test Organization'
        )
        
        # Valid credentials
        user = auth_service.authenticate_user('auth_test@example.com', 'password123')
        assert user is not None
        assert user.email == 'auth_test@example.com'
        assert user.role == 'borrower'
        assert user.full_name == 'Auth Test'
        assert user.phone_number == '1234567890'
        assert user.organization == 'Test Organization'
        assert user.check_password('password123') is True  # Fixed: checking correct password
        
        # Invalid email
        with pytest.raises(ValueError):
            auth_service.authenticate_user('wrong@example.com', 'password123')
            
        # Invalid password
        with pytest.raises(ValueError):
            auth_service.authenticate_user('auth_test@example.com', 'wrongpassword')