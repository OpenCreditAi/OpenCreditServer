from app.models.user import User

def test_user_creation():
    user = User(
        email='test@example.com',
        role='borrower',
        full_name='Test User',
        phone_number='1234567890',
        organization='Test Organization'
    )
    assert user.email == 'test@example.com'
    assert user.role == 'borrower'
    assert user.full_name == 'Test User'
    assert user.phone_number == '1234567890'
    assert user.organization == 'Test Organization'

def test_password_hashing():
    user = User(
        email='test@example.com',
        role='borrower',
        full_name='Test User',
        phone_number='1234567890',
        organization='Test Organization'
    )
    user.set_password('password123')
    
    assert user.password_hash is not None
    assert user.check_password('password123') is True
    assert user.check_password('wrongpassword') is False