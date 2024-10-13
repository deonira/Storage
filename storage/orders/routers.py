from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import Order, OrderItem
from .schemas import OrderCreate, OrderResponse
from storage.database import SessionLocal
from ..products.models import Product

api_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@api_router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    order_items = []

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found.")

        if product.quantity_in_stock < item.quantity:
            raise HTTPException(status_code=400,
                                detail=f"Not enough stock for product {product.name}. Available: {product.quantity_in_stock}, Required: {item.quantity}")

        product.quantity_in_stock -= item.quantity
        db.add(product)

        order_item = OrderItem(product_id=product.id, quantity=item.quantity)
        order_items.append(order_item)

    new_order = Order()
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order_items:
        item.order_id = new_order.id
        db.add(item)
    db.commit()

    return {
        "id": new_order.id,
        "created_at": new_order.created_at,
        "status": new_order.status,
        "items": [{"id": item.id, "product_id": item.product_id, "quantity": item.quantity} for item in order_items]
    }

@api_router.get("/orders", response_model=List[OrderResponse])
async def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@api_router.get("/orders/{id}", response_model=OrderResponse)
async def get_order(id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@api_router.patch("/orders/{id}", response_model=OrderResponse)
async def update_order(id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    db.commit()
    db.refresh(order)
    return order


@api_router.delete("/orders/{id}")
async def delete_order(id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    db.commit()
    return {"detail": "Order deleted"}