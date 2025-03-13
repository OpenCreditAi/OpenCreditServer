from app.models.user import User

def test_user_creation():
    user = User(email='test@example.com', role='borrower')
    assert user.email == 'test@example.com'
    assert user.role == 'borrower'

def test_password_hashing():
    user = User(email='test@example.com', role='borrower')
    user.set_password('password123')
    
    assert user.password_hash is not None
    assert user.password_hash != 'password123'
    assert user.check_password('password123') is True
    assert user.check_password('wrongpassword') is False