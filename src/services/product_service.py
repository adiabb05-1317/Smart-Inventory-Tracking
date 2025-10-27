from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal


class ProductService:
    """Business logic layer for product operations."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_products_with_filters(
        self,
        category: Optional[str] = None,
        price_min: Optional[Decimal] = None,
        price_max: Optional[Decimal] = None,
        in_stock: Optional[bool] = None,
        sort_by: str = "id",
        order: str = "asc"
    ) -> List[Tuple]:
        """Get products with advanced filtering and sorting."""
        valid_sort_columns = ["id", "name", "price", "stock_quantity", "created_at"]
        valid_orders = ["asc", "desc"]
        
        if sort_by not in valid_sort_columns:
            sort_by = "id"
        if order.lower() not in valid_orders:
            order = "asc"
        
        where_clauses = []
        params = []
        
        if category:
            where_clauses.append("category = %s")
            params.append(category)
        
        if price_min is not None:
            where_clauses.append("price >= %s")
            params.append(price_min)
        
        if price_max is not None:
            where_clauses.append("price <= %s")
            params.append(price_max)
        
        if in_stock is not None:
            if in_stock:
                where_clauses.append("stock_quantity > 0")
            else:
                where_clauses.append("stock_quantity = 0")
        
        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
            SELECT id, name, category, price, stock_quantity, reorder_level, 
                   last_restocked, created_at, updated_at, supplier, warranty_months
            FROM products
            {where_sql}
            ORDER BY {sort_by} {order.upper()}
        """
        
        return self.db_manager.fetch_all(query, tuple(params) if params else None)
    
    def bulk_create_products(self, products_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk create products with validation."""
        created_count = 0
        failed_count = 0
        failures = []
        
        for idx, product in enumerate(products_data):
            try:
                query = """
                    INSERT INTO products 
                    (name, category, price, stock_quantity, reorder_level, supplier, warranty_months, last_restocked)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """
                self.db_manager.execute_query(
                    query,
                    (
                        product["name"],
                        product["category"],
                        product["price"],
                        product["stock_quantity"],
                        product.get("reorder_level", 10),
                        product.get("supplier"),
                        product.get("warranty_months", 12)
                    )
                )
                created_count += 1
            except Exception as e:
                failed_count += 1
                failures.append({"index": idx, "error": str(e), "product_name": product.get("name", "unknown")})
        
        return {
            "created_count": created_count,
            "failed_count": failed_count,
            "failures": failures
        }
    
    def bulk_restock_products(self, restock_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk restock products."""
        updated_count = 0
        errors = []
        
        for item in restock_data:
            try:
                product_id = item["product_id"]
                quantity = item["quantity"]
                
                # Check if product exists
                check_query = "SELECT id FROM products WHERE id = %s"
                result = self.db_manager.fetch_one(check_query, (product_id,))
                
                if not result:
                    errors.append({
                        "product_id": product_id,
                        "error": f"Product with id {product_id} not found"
                    })
                    continue
                
                # Update stock
                update_query = """
                    UPDATE products
                    SET stock_quantity = stock_quantity + %s,
                        last_restocked = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                self.db_manager.execute_query(update_query, (quantity, product_id))
                updated_count += 1
                
            except Exception as e:
                errors.append({
                    "product_id": item.get("product_id"),
                    "error": str(e)
                })
        
        return {
            "updated_count": updated_count,
            "errors": errors
        }
    
    def record_sale(self, product_id: int, quantity: int, sale_price: Decimal) -> Dict[str, Any]:
        """Record a sale and reduce product stock."""
        # Get current product stock
        product_query = """
            SELECT id, stock_quantity, name
            FROM products
            WHERE id = %s
        """
        product = self.db_manager.fetch_one(product_query, (product_id,))
        
        if not product:
            raise ValueError(f"Product with id {product_id} not found")
        
        current_stock = product[1]
        product_name = product[2]
        
        if current_stock < quantity:
            raise ValueError(
                f"Insufficient stock for {product_name}. "
                f"Available: {current_stock}, Requested: {quantity}"
            )
        
        # Insert sale record
        sale_query = """
            INSERT INTO sales_history (product_id, quantity_sold, sale_price, sale_date)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        """
        sale_result = self.db_manager.fetch_one(sale_query, (product_id, quantity, sale_price))
        sale_id = sale_result[0] if sale_result else None
        
        # Reduce stock quantity
        update_query = """
            UPDATE products
            SET stock_quantity = stock_quantity - %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING stock_quantity
        """
        result = self.db_manager.fetch_one(update_query, (quantity, product_id))
        remaining_stock = result[0] if result else 0
        
        return {
            "sale_id": sale_id,
            "product_name": product_name,
            "quantity_sold": quantity,
            "remaining_stock": remaining_stock
        }

