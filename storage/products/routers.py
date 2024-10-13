from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import Product
from .schemas import ProductCreate, ProductResponse
from ..database import SessionLocal

api_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@api_router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@api_router.get("/products", response_model=List[ProductResponse])
async def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@api_router.get("/products/{id}", response_model=ProductResponse)
async def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@api_router.put("/products/{id}", response_model=ProductResponse)
async def update_product(id: int, product: ProductCreate, db: Session = Depends(get_db)):
    existing_product = db.query(Product).filter(Product.id == id).first()
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.model_dump().items():
        setattr(existing_product, key, value)

    db.commit()
    db.refresh(existing_product)
    return existing_product

@api_router.delete("/products/{id}")
async def delete_product(id: int, db: Session = Depends(get_db)):
    existing_product = db.query(Product).filter(Product.id == id).first()
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(existing_product)
    db.commit()
    return {"detail": "Product deleted"}