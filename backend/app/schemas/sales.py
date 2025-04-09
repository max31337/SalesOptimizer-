from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SaleBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    total_amount: float
    status: Optional[str] = "completed"

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    user_id: int
    transaction_date: datetime
    product: Product

    class Config:
        orm_mode = True

class SalesAnalytics(BaseModel):
    total_sales: float
    total_transactions: int
    average_transaction_value: float
    sales_by_category: dict
    sales_trend: List[dict]