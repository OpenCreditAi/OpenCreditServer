import json

def test_signup_success(client):
    response = client.post('/auth/signup', json={
        'email': 'newuser@example.com',
        'password': 'securepassword',
        'role': 'borrower',
        'fullName': 'New User',
        'phoneNumber': '1234567890',
        'organization': 'New Corp Ltd'
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'access_token' in data
    assert data['user']['email'] == 'newuser@example.com'
    assert data['user']['role'] == 'borrower'
    assert data['user']['fullName'] == 'New User'
    assert data['user']['phoneNumber'] == '1234567890'
    assert data['user']['organization'] == 'New Corp Ltd'

def test_signup_missing_fields(client):
    response = client.post('/auth/signup', json={
        'email': 'incomplete@example.com',
        'password': 'securepassword'
        # Missing required fields
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_signup_duplicate_email(client, test_user):
    response = client.post('/auth/signup', json={
        'email': 'test@example.com',  # Same as test_user
        'password': 'different_password',
        'role': 'financier',
        'fullName': 'Another User',
        'phoneNumber': '0987654321',
        'organization': 'Another Corp'
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'already registered' in data['error']

def test_signin_success(client, test_user):
    response = client.post('/auth/signin', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    # Note: Your signin route doesn't return user data currently

def test_signin_invalid_credentials(client):
    response = client.post('/auth/signin', json={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data