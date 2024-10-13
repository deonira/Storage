from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(
        from_attributes=True
    )

class OrderResponse(BaseModel):
    id: int
    created_at: datetime
    status: str
    items: List[OrderItemResponse]

    model_config = ConfigDict(
        from_attributes=True
    )