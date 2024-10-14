import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from storage.database import Base, get_db
from storage.orders.schemas import OrderItemCreate
from fastapi import Depends
from pydantic import ValidationError

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:123456@db:5432/test_storagedb")
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_test_db():
    Base.metadata.create_all(bind=engine)

def drop_test_db():
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_test_db()
    yield
    drop_test_db()

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
    assert response.json()["status"] == "in process"

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

def test_order_item_quantity_positive():
    valid_data = {
        "product_id": 1,
        "quantity": 5
    }
    item = OrderItemCreate(**valid_data)
    assert item.quantity == 5

def test_order_item_quantity_negative():
    invalid_data = {
        "product_id": 1,
        "quantity": -1
    }
    with pytest.raises(ValidationError) as exc_info:
        OrderItemCreate(**invalid_data)

    assert "Quantity must be greater than zero" in str(exc_info.value)

def test_order_item_quantity_zero():
    invalid_data = {
        "product_id": 1,
        "quantity": 0
    }
    with pytest.raises(ValidationError) as exc_info:
        OrderItemCreate(**invalid_data)

    assert "Quantity must be greater than zero" in str(exc_info.value)
