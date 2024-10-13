from pydantic import BaseModel, ConfigDict
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity_in_stock: int

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    quantity_in_stock: int

    model_config = ConfigDict(
        from_attributes=True
    )