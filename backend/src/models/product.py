from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    """Base product schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")
    price: Decimal = Field(..., gt=0, description="Product price")
    stock_quantity: int = Field(..., ge=0, description="Current stock quantity")
    reorder_level: int = Field(default=10, ge=0, description="Minimum stock level before reorder")
    supplier: Optional[str] = Field(None, max_length=100, description="Supplier name")
    warranty_months: int = Field(default=12, ge=0, description="Warranty period in months")


class ProductCreate(ProductBase):
    """
    Product creation schema.
    
    Example:
    ```json
    {
        "name": "iPhone 15 Pro",
        "category": "Smartphones",
        "price": 999.99,
        "stock_quantity": 50,
        "reorder_level": 15,
        "supplier": "Apple Inc.",
        "warranty_months": 12
    }
    ```
    """
    pass


class ProductUpdate(BaseModel):
    """Product update schema - all fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    supplier: Optional[str] = Field(None, max_length=100)
    warranty_months: Optional[int] = Field(None, ge=0)


class ProductResponse(ProductBase):
    """
    Product response schema.
    
    Example:
    ```json
    {
        "id": 1,
        "name": "iPhone 15 Pro",
        "category": "Smartphones",
        "price": 999.99,
        "stock_quantity": 50,
        "reorder_level": 15,
        "supplier": "Apple Inc.",
        "warranty_months": 12,
        "last_restocked": "2024-01-15T10:30:00",
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-15T10:30:00"
    }
    ```
    """
    id: int
    last_restocked: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

