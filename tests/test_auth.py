def test_register_new_user(client):
    response = client.post("/auth/register", json={"username": "newuser", "password": "pass123"})
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"

def test_login_valid_credentials(client):
    client.post("/auth/register", json={"username": "logintest", "password": "pass123"})
    response = client.post("/auth/login", json={"username": "logintest", "password": "pass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "wrongtest", "password": "pass123"})
    response = client.post("/auth/login", json={"username": "wrongtest", "password": "wrong"})
    assert response.status_code == 401
