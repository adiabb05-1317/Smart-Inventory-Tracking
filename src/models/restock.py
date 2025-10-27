from pydantic import BaseModel, Field
from typing import List


class RestockRequest(BaseModel):
    """
    Restock request schema.
    
    Example:
    ```json
    {
        "quantity": 50
    }
    ```
    """
    quantity: int = Field(..., gt=0, description="Quantity to add to stock")


class BulkRestockItem(BaseModel):
    """Single item in bulk restock request."""
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity to add")


class BulkRestockRequest(BaseModel):
    """
    Bulk restock request schema.
    
    Example:
    ```json
    {
        "items": [
            {"product_id": 1, "quantity": 50},
            {"product_id": 2, "quantity": 30}
        ]
    }
    ```
    """
    items: List[BulkRestockItem]

