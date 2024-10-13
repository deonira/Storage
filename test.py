from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_orders():
    response = client.get("/orders")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        assert "id" in response.json()[0]
        assert "created_at" in response.json()[0]
        assert "status" in response.json()[0]
        assert "items" in response.json()[0]


def test_create_product():
    response = client.post(
        "/products",
        json={
            "name": "Test Product",
            "description": "This is a test product.",
            "price": 10.0,
            "quantity_in_stock": 100,
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Product"


def test_get_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_order():
    client.post(
        "/products",
        json={
            "name": "Test Product",
            "description": "This is a test product.",
            "price": 10.0,
            "quantity_in_stock": 100,
        },
    )

    response = client.post(
        "/orders",
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        },
    )
    assert response.status_code == 201
    assert response.json()["status"] == "в процессе"


def test_order_insufficient_stock():
    response = client.post(
        "/orders",
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1000
                }
            ]
        },
    )
    assert response.status_code == 400
    assert "Not enough stock" in response.json()["detail"]