import pytest
from tests.test_config import client, init_test_db, cleanup_test_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_test_db()
    yield
    cleanup_test_db()

def test_register_new_user():
    response = client.post("/auth/register", json={
        "username": "new_user_test",
        "password": "strongpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "new_user_test"
    assert "id" in data

def test_register_existing_user():

    client.post("/auth/register", json={"username": "duplicate", "password": "123"})
    response = client.post("/auth/register", json={"username": "duplicate", "password": "123"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login_successful():
    client.post("/auth/register", json={"username": "login_user", "password": "123"})
    response = client.post("/auth/login", data={
        "username": "login_user",
        "password": "123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post("/auth/login", data={
        "username": "non_existent",
        "password": "wrong_password"
    })
    assert response.status_code == 401