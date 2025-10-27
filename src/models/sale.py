from pydantic import BaseModel, Field
from decimal import Decimal


class SaleRequest(BaseModel):
    """
    Sales transaction request schema.
    
    Example:
    ```json
    {
        "product_id": 1,
        "quantity_sold": 5,
        "sale_price": 999.99
    }
    ```
    """
    product_id: int = Field(..., description="Product ID")
    quantity_sold: int = Field(..., gt=0, description="Quantity sold")
    sale_price: Decimal = Field(..., gt=0, description="Sale price per unit")


class SaleResponse(BaseModel):
    """
    Sales transaction response schema.
    
    Example:
    ```json
    {
        "sale_id": 42,
        "product_name": "iPhone 15 Pro",
        "quantity_sold": 5,
        "remaining_stock": 40
    }
    ```
    """
    sale_id: int
    product_name: str
    quantity_sold: int
    remaining_stock: int

