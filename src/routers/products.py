from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

router = APIRouter(prefix="/products", tags=["products"])


# Pydantic Models
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")
    price: Decimal = Field(..., gt=0, description="Product price")
    stock_quantity: int = Field(..., ge=0, description="Current stock quantity")
    reorder_level: int = Field(default=10, ge=0, description="Minimum stock level before reorder")


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
        "reorder_level": 15
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


# Helper function to convert DB row to ProductResponse
def row_to_product(row) -> ProductResponse:
    """Convert database row tuple to ProductResponse model."""
    return ProductResponse(
        id=row[0],
        name=row[1],
        category=row[2],
        price=row[3],
        stock_quantity=row[4],
        reorder_level=row[5],
        last_restocked=row[6],
        created_at=row[7],
        updated_at=row[8]
    )


@router.get("", response_model=List[ProductResponse], summary="Get all products")
async def get_products(request: Request, low_stock: Optional[bool] = None):
    """
    Get all products with optional filtering for low stock.
    
    - **low_stock**: If true, returns only products below reorder level
    """
    db_manager = request.app.state.db_manager
    
    try:
        if low_stock:
            query = """
                SELECT id, name, category, price, stock_quantity, reorder_level, 
                       last_restocked, created_at, updated_at
                FROM products
                WHERE stock_quantity < reorder_level
                ORDER BY stock_quantity ASC
            """
        else:
            query = """
                SELECT id, name, category, price, stock_quantity, reorder_level, 
                       last_restocked, created_at, updated_at
                FROM products
                ORDER BY id ASC
            """
        
        rows = db_manager.fetch_all(query)
        return [row_to_product(row) for row in rows]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/low-stock", response_model=List[ProductResponse], summary="Get low stock products")
async def get_low_stock_products(request: Request):
    """
    Get all products that are below their reorder level.
    Returns products sorted by stock quantity (lowest first).
    """
    db_manager = request.app.state.db_manager
    
    try:
        query = """
            SELECT id, name, category, price, stock_quantity, reorder_level, 
                   last_restocked, created_at, updated_at
            FROM products
            WHERE stock_quantity < reorder_level
            ORDER BY stock_quantity ASC
        """
        
        rows = db_manager.fetch_all(query)
        return [row_to_product(row) for row in rows]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/{product_id}", response_model=ProductResponse, summary="Get product by ID")
async def get_product(product_id: int, request: Request):
    """
    Get a specific product by ID.
    
    - **product_id**: The ID of the product to retrieve
    """
    db_manager = request.app.state.db_manager
    
    try:
        query = """
            SELECT id, name, category, price, stock_quantity, reorder_level, 
                   last_restocked, created_at, updated_at
            FROM products
            WHERE id = %s
        """
        
        row = db_manager.fetch_one(query, (product_id,))
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        
        return row_to_product(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Create new product")
async def create_product(product: ProductCreate, request: Request):
    """
    Create a new product in the inventory.
    
    Example request body:
    ```json
    {
        "name": "iPhone 15 Pro",
        "category": "Smartphones",
        "price": 999.99,
        "stock_quantity": 50,
        "reorder_level": 15
    }
    ```
    """
    db_manager = request.app.state.db_manager
    
    try:
        query = """
            INSERT INTO products (name, category, price, stock_quantity, reorder_level, last_restocked)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, name, category, price, stock_quantity, reorder_level, 
                      last_restocked, created_at, updated_at
        """
        
        row = db_manager.fetch_one(
            query,
            (product.name, product.category, product.price, product.stock_quantity, product.reorder_level)
        )
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create product"
            )
        
        return row_to_product(row)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.put("/{product_id}", response_model=ProductResponse, summary="Update product")
async def update_product(product_id: int, product: ProductUpdate, request: Request):
    """
    Update an existing product.
    All fields are optional - only provided fields will be updated.
    
    - **product_id**: The ID of the product to update
    """
    db_manager = request.app.state.db_manager
    
    # Check if product exists
    check_query = "SELECT id FROM products WHERE id = %s"
    existing = db_manager.fetch_one(check_query, (product_id,))
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    # Build dynamic update query based on provided fields
    update_fields = []
    params = []
    
    if product.name is not None:
        update_fields.append("name = %s")
        params.append(product.name)
    if product.category is not None:
        update_fields.append("category = %s")
        params.append(product.category)
    if product.price is not None:
        update_fields.append("price = %s")
        params.append(product.price)
    if product.stock_quantity is not None:
        update_fields.append("stock_quantity = %s")
        params.append(product.stock_quantity)
    if product.reorder_level is not None:
        update_fields.append("reorder_level = %s")
        params.append(product.reorder_level)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )
    
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(product_id)
    
    try:
        query = f"""
            UPDATE products
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, name, category, price, stock_quantity, reorder_level, 
                      last_restocked, created_at, updated_at
        """
        
        row = db_manager.fetch_one(query, tuple(params))
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update product"
            )
        
        return row_to_product(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete product")
async def delete_product(product_id: int, request: Request):
    """
    Delete a product from the inventory.
    
    - **product_id**: The ID of the product to delete
    """
    db_manager = request.app.state.db_manager
    
    # Check if product exists
    check_query = "SELECT id FROM products WHERE id = %s"
    existing = db_manager.fetch_one(check_query, (product_id,))
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    try:
        query = "DELETE FROM products WHERE id = %s"
        db_manager.execute_query(query, (product_id,))
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.post("/{product_id}/restock", response_model=ProductResponse, summary="Restock product")
async def restock_product(product_id: int, restock: RestockRequest, request: Request):
    """
    Add stock quantity to an existing product and update last_restocked timestamp.
    
    - **product_id**: The ID of the product to restock
    - **quantity**: The quantity to add to current stock
    
    Example request body:
    ```json
    {
        "quantity": 50
    }
    ```
    """
    db_manager = request.app.state.db_manager
    
    # Check if product exists
    check_query = "SELECT id FROM products WHERE id = %s"
    existing = db_manager.fetch_one(check_query, (product_id,))
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    try:
        query = """
            UPDATE products
            SET stock_quantity = stock_quantity + %s,
                last_restocked = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, name, category, price, stock_quantity, reorder_level, 
                      last_restocked, created_at, updated_at
        """
        
        row = db_manager.fetch_one(query, (restock.quantity, product_id))
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to restock product"
            )
        
        return row_to_product(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

