from langchain.tools import BaseTool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..product_service import ProductService


class InventoryQueryTool(BaseTool):
    name: str = "inventory_query"
    description: str = """Query product inventory information. Use this to:
    - Get all products or filter by category
    - Check stock levels for specific products
    - Find low stock items
    Input should be a query like 'all products' or 'low stock items' or 'category:Smartphones'
    """

    def __init__(self, product_service):
        super().__init__()
        self._product_service = product_service
    
    def _run(self, query: str) -> str:
        try:
            if "low stock" in query.lower():
                # Get products where stock < reorder_level
                products = self._product_service.get_products_with_filters()
                low_stock = [p for p in products if p[4] < p[5]]  # stock_quantity < reorder_level
                
                if not low_stock:
                    return "No low stock items found."
                
                result = f"Found {len(low_stock)} low stock items:\n"
                for p in low_stock[:5]:
                    result += f"- {p[1]}: ${p[3]}, Stock: {p[4]} (Reorder at: {p[5]})\n"
                
                if len(low_stock) > 5:
                    result += f"...and {len(low_stock) - 5} more items"
                return result
                
            elif "category:" in query.lower():
                category = query.split("category:")[1].strip()
                products = self._product_service.get_products_with_filters(category=category)
                
                if not products:
                    return f"No products found in category: {category}"
                
                result = f"Found {len(products)} products in {category}:\n"
                for p in products[:5]:
                    result += f"- {p[1]}: ${p[3]}, Stock: {p[4]}\n"
                
                if len(products) > 5:
                    result += f"...and {len(products) - 5} more products"
                return result
            else:
                products = self._product_service.get_products_with_filters()
                
                if not products:
                    return "No products found."
                
                result = f"Found {len(products)} products:\n"
                for p in products[:5]:
                    result += f"- {p[1]} ({p[2]}): ${p[3]}, Stock: {p[4]}\n"
                
                if len(products) > 5:
                    result += f"...and {len(products) - 5} more products"
                return result
        
        except Exception as e:
            return f"Error querying inventory: {str(e)}"
