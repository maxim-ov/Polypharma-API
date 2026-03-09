def test_signup_success(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strongpassword"
        }
    )
    assert response.status_code == 201
    assert response.json()["message"] == "User 'newuser' registered successfully."

def test_signup_duplicate_username(client):
    # First signup
    client.post(
        "/auth/signup",
        json={"username": "dupuser", "email": "dup@example.com", "password": "pw"}
    )
    # Second signup with same username
    response = client.post(
        "/auth/signup",
        json={"username": "dupuser", "email": "other@example.com", "password": "pw"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"

def test_signup_duplicate_email(client):
    # First signup
    client.post(
        "/auth/signup",
        json={"username": "user1", "email": "shared@example.com", "password": "pw"}
    )
    # Second signup with same email
    response = client.post(
        "/auth/signup",
        json={"username": "user2", "email": "shared@example.com", "password": "pw"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client, db_session):
    # Seed user via client or fixture, here we use client since DB state gets cleaned each test
    client.post(
        "/auth/signup",
        json={"username": "loginuser", "email": "log@example.com", "password": "pw"}
    )
    
    # Attempt login
    response = client.post(
        "/auth/login",
        json={"username": "loginuser", "password": "pw"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    client.post(
        "/auth/signup",
        json={"username": "wrongpassuser", "email": "wrong@example.com", "password": "pw"}
    )
    
    response = client.post(
        "/auth/login",
        json={"username": "wrongpassuser", "password": "invalidpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

def test_login_unknown_user(client):
    response = client.post(
        "/auth/login",
        json={"username": "ghost", "password": "pw"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"
