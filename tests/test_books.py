import pytest
from tests.test_config import client, init_test_db, cleanup_test_db, TestingSessionLocal

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_test_db()
    yield
    cleanup_test_db()

def get_admin_headers():

    login_data = {"username": "test_admin", "password": "password", "role": "admin"}
    client.post("/auth/register", json={"username": "test_admin", "password": "password"})
    
    db = TestingSessionLocal()
    from app.models import User
    user = db.query(User).filter(User.username == "test_admin").first()
    if user:
        user.role = "admin"
        db.commit()
    db.close()

    response = client.post("/auth/login", data={"username": "test_admin", "password": "password"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def get_user_headers():
    login_data = {"username": "test_user_normal", "password": "password"}
    client.post("/auth/register", json=login_data)
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_list_books_empty_db():
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_book():
    admin_headers = get_admin_headers()
    new_book = {
        "title": "Testowa Książka",
        "author": "Testowy Autor",
        "description": "Testowy opis książki.",
        "year": 2026
    }
    response = client.post("/books/", json=new_book, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == new_book["title"]
    assert data["author"] == new_book["author"]

def test_create_book_optional_fields_none():
    admin_headers = get_admin_headers()
    minimal_book = {"title": "Przykładowa nazwa", "author": "Autor"}
    response = client.post("/books/", json=minimal_book, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] is None
    assert data["year"] is None

def test_create_book_invalid_missing_field():
    admin_headers = get_admin_headers()
    incomplete_book = {"title": "Tylko tytuł"}  # missing author
    response = client.post("/books/", json=incomplete_book, headers=admin_headers)
    assert response.status_code == 422

def test_create_book_invalid_type():
    admin_headers = get_admin_headers()
    invalid_book = {
        "title": "Tytuł",
        "author": "Autor",
        "description": "Opis książki",
        "year": "Nieprawidłowy rok"
    }
    response = client.post("/books/", json=invalid_book, headers=admin_headers)
    assert response.status_code == 422

def test_update_book():
    admin_headers = get_admin_headers()
    create_resp = client.post("/books/", json={
        "title": "Stary Tytul",
        "author": "Autor",
        "year": 2000,
        "description": "Opis"
    }, headers=admin_headers)

    book_id = create_resp.json()["id"]

    user_headers = get_user_headers()

    update_data = {
        "title": "Nowy Tytul",
        "year": 2025
    }

    response = client.put(f"/books/{book_id}", json=update_data, headers=user_headers)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Nowy Tytul"
    assert data["year"] == 2025
    assert data["author"] == "Autor"

def test_update_book_unauthorized():

    admin_headers = get_admin_headers()
    create_resp = client.post("/books/", json={
        "title": "Do Zmiany",
        "author": "Autor"
    }, headers=admin_headers)

    book_id = create_resp.json()["id"]
    update_data = {"title": "Zmiana tytułu"}
    
    response = client.put(f"/books/{book_id}", json=update_data)
    assert response.status_code == 401

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text

def test_delete_book_as_admin():
    admin_headers = get_admin_headers()
    create_resp = client.post("/books/", json={"title": "Do Usuniecia", "author": "X"}, headers=admin_headers)
    book_id = create_resp.json()["id"]

    del_resp = client.delete(f"/books/{book_id}", headers=admin_headers)
    assert del_resp.status_code == 204
    
    get_resp = client.get("/books/")
    books = get_resp.json()

    assert not any(b['id'] == book_id for b in books)

def test_delete_book_as_user_forbidden():
    admin_headers = get_admin_headers()
    create_resp = client.post("/books/", json={"title": "Nie rusz", "author": "X"}, headers=admin_headers)
    book_id = create_resp.json()["id"]

    user_headers = get_user_headers()
    del_resp = client.delete(f"/books/{book_id}", headers=user_headers)
    
    assert del_resp.status_code == 403