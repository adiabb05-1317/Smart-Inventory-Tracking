from fastapi import APIRouter, HTTPException, status, Request, Query
from typing import Optional, List
from decimal import Decimal
from src.services.product_service import ProductService
from src.models import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    RestockRequest,
    BulkRestockRequest,
    SaleRequest
)

router = APIRouter(prefix="/products", tags=["products"])


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
        updated_at=row[8],
        supplier=row[9] if len(row) > 9 else None,
        warranty_months=row[10] if len(row) > 10 else 12
    )


@router.get("", response_model=List[ProductResponse], summary="Get all products with filtering")
async def get_products(
    request: Request,
    low_stock: Optional[bool] = None,
    category: Optional[str] = Query(None, description="Filter by category"),
    price_min: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    price_max: Optional[Decimal] = Query(None, gt=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    sort_by: str = Query("id", description="Sort by: id, name, price, stock_quantity"),
    order: str = Query("asc", description="Sort order: asc, desc")
):
    """
    Get all products with advanced filtering and sorting.
    
    **Parameters:**
    - **low_stock**: If true, returns only products below reorder level
    - **category**: Filter by product category
    - **price_min**: Minimum price filter
    - **price_max**: Maximum price filter
    - **in_stock**: Filter by stock availability (true=in stock, false=out of stock)
    - **sort_by**: Sort by field (id, name, price, stock_quantity)
    - **order**: Sort order (asc, desc)
    
    **Example:**
    ```
    GET /products?category=Smartphones&price_max=1000&sort_by=price&order=asc
    ```
    """
    # Validate price filters
    if price_min is not None and price_max is not None and price_max <= price_min:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="price_max must be greater than price_min"
        )
    
    try:
        if low_stock:
            query = """
                SELECT id, name, category, price, stock_quantity, reorder_level, 
                       last_restocked, created_at, updated_at, supplier, warranty_months
                FROM products
                WHERE stock_quantity < reorder_level
                ORDER BY stock_quantity ASC
            """
            rows = request.app.state.db_manager.fetch_all(query)
        else:
            product_service = ProductService(request.app.state.db_manager)
            rows = product_service.get_products_with_filters(
                category=category,
                price_min=price_min,
                price_max=price_max,
                in_stock=in_stock,
                sort_by=sort_by,
                order=order
            )
        
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
                   last_restocked, created_at, updated_at, supplier, warranty_months
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
                   last_restocked, created_at, updated_at, supplier, warranty_months
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
        "reorder_level": 15,
        "supplier": "Apple Inc.",
        "warranty_months": 12
    }
    ```
    """
    db_manager = request.app.state.db_manager
    
    try:
        query = """
            INSERT INTO products (name, category, price, stock_quantity, reorder_level, supplier, warranty_months, last_restocked)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, name, category, price, stock_quantity, reorder_level, 
                      last_restocked, created_at, updated_at, supplier, warranty_months
        """
        
        row = db_manager.fetch_one(
            query,
            (product.name, product.category, product.price, product.stock_quantity, 
             product.reorder_level, product.supplier, product.warranty_months)
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
    if product.supplier is not None:
        update_fields.append("supplier = %s")
        params.append(product.supplier)
    if product.warranty_months is not None:
        update_fields.append("warranty_months = %s")
        params.append(product.warranty_months)
    
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
                      last_restocked, created_at, updated_at, supplier, warranty_months
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
                      last_restocked, created_at, updated_at, supplier, warranty_months
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


# Bulk Operations and Sales Endpoints

@router.post("/bulk-upload", status_code=status.HTTP_201_CREATED, tags=["Products", "Bulk Operations"], summary="Bulk upload products")
async def bulk_upload_products(products: List[ProductCreate], request: Request):
    """
    Bulk upload multiple products at once.
    
    Validates each product and inserts all valid products.
    Returns a report of successes and failures.
    
    **Request Body:**
    Array of product objects
    
    **Example:**
    ```json
    [
        {
            "name": "AirPods Pro 2",
            "category": "Audio",
            "price": 249.99,
            "stock_quantity": 35,
            "reorder_level": 20,
            "supplier": "Apple Inc.",
            "warranty_months": 12
        },
        {
            "name": "Google Pixel 8",
            "category": "Smartphones",
            "price": 699.99,
            "stock_quantity": 25,
            "reorder_level": 15,
            "supplier": "Google LLC",
            "warranty_months": 24
        }
    ]
    ```
    
    **Response:**
    ```json
    {
        "created_count": 2,
        "failed_count": 0,
        "failures": []
    }
    ```
    """
    try:
        product_service = ProductService(request.app.state.db_manager)
        products_data = [product.dict() for product in products]
        result = product_service.bulk_create_products(products_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during bulk upload: {str(e)}"
        )


@router.put("/bulk-restock", tags=["Products", "Bulk Operations"], summary="Bulk restock products")
async def bulk_restock_products(restock_request: BulkRestockRequest, request: Request):
    """
    Bulk restock multiple products at once.
    
    Updates stock quantities and last_restocked timestamp for each product.
    
    **Request Body:**
    ```json
    {
        "items": [
            {"product_id": 1, "quantity": 50},
            {"product_id": 2, "quantity": 30},
            {"product_id": 3, "quantity": 20}
        ]
    }
    ```
    
    **Response:**
    ```json
    {
        "updated_count": 3,
        "errors": []
    }
    ```
    """
    try:
        product_service = ProductService(request.app.state.db_manager)
        restock_data = [item.dict() for item in restock_request.items]
        result = product_service.bulk_restock_products(restock_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during bulk restock: {str(e)}"
        )


@router.post("/sales", status_code=status.HTTP_201_CREATED, summary="Record a sale")
async def record_sale(sale: SaleRequest, request: Request):
    """
    Record a sales transaction.
    
    - Validates sufficient stock availability
    - Records sale in sales_history table
    - Reduces product stock quantity
    - Clears analytics cache to reflect new data
    - Returns updated stock information
    
    **Request Body:**
    ```json
    {
        "product_id": 1,
        "quantity_sold": 5,
        "sale_price": 999.99
    }
    ```
    
    **Response:**
    ```json
    {
        "sale_id": 42,
        "product_name": "iPhone 15 Pro",
        "quantity_sold": 5,
        "remaining_stock": 40
    }
    ```
    
    **Errors:**
    - 404: Product not found
    - 400: Insufficient stock
    """
    try:
        product_service = ProductService(request.app.state.db_manager)
        result = product_service.record_sale(
            sale.product_id,
            sale.quantity_sold,
            sale.sale_price
        )
        
        # Clear analytics cache since sales data has changed
        request.app.state.cache.clear(pattern="sales_trends")
        request.app.state.cache.clear(pattern="top_performers")
        
        return result
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording sale: {str(e)}"
        )

