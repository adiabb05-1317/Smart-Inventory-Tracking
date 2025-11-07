from langchain.tools import BaseTool
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ...db.db_manager import DBManager


class SQLExecutorTool(BaseTool):
    name: str = "sql_executor"
    description: str = """Execute SQL queries on the inventory database to answer questions.
    
    Available tables:
    - products (id, name, category, price, stock_quantity, reorder_level, supplier, warranty_months, last_restocked, created_at, updated_at)
    - sales_history (id, product_id, quantity_sold, sale_price, sale_date)
    
    Use this tool to:
    - Count products: "SELECT COUNT(*) FROM products"
    - Get low stock: "SELECT name, stock_quantity FROM products WHERE stock_quantity < reorder_level"
    - Get products by category: "SELECT * FROM products WHERE category = 'Smartphones'"
    - Get sales trends: "SELECT DATE(sale_date), SUM(quantity_sold * sale_price) as revenue FROM sales_history WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY DATE(sale_date)"
    - Get top performers: "SELECT p.name, SUM(s.quantity_sold) as total_sales FROM products p JOIN sales_history s ON p.id = s.product_id GROUP BY p.name ORDER BY total_sales DESC LIMIT 5"
    
    Input: A valid SQL SELECT query (READ-ONLY, no INSERT/UPDATE/DELETE)
    Output: Query results as formatted text
    """
    
    db_manager: Optional[Any] = None
    
    def _clean_query(self, query: str) -> str:
        if not query:
            return ""

        cleaned = query.strip()

        # Remove any agent markup that might have been concatenated
        markers = [
            "Observation:",
            "Observation",
            "Thought:",
            "Action:",
            "Action Input:",
            "Final Answer:"
        ]

        for marker in markers:
            idx = cleaned.find(marker)
            if idx != -1:
                cleaned = cleaned[:idx].strip()

        # Strip trailing backticks or stray quotes
        cleaned = cleaned.strip("`\"")

        return cleaned

    def _run(self, query: str) -> str:
        cleaned_query = self._clean_query(query)
        if not cleaned_query:
            return "Error: No valid SQL query provided."

        try:
            # Security: Only allow SELECT queries
            query_upper = cleaned_query.upper()
            if not query_upper.startswith('SELECT'):
                return "Error: Only SELECT queries are allowed for security reasons."
            
            # Block dangerous keywords
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
            if any(keyword in query_upper for keyword in dangerous_keywords):
                return "Error: Query contains forbidden operations."
            
            # Execute query
            results = self.db_manager.fetch_all(cleaned_query)
            
            if not results:
                return "No results found."
            
            # Format results
            if len(results) == 1 and len(results[0]) == 1:
                # Single value result
                return f"Result: {results[0][0]}"
            
            # Multiple rows/columns
            output = f"Found {len(results)} result(s):\n\n"
            
            for idx, row in enumerate(results[:10], 1):  # Limit to 10 rows
                output += f"{idx}. "
                output += " | ".join(str(val) for val in row)
                output += "\n"
            
            if len(results) > 10:
                output += f"\n...and {len(results) - 10} more rows"
            
            return output
            
        except Exception as e:
            return f"Error executing query: {str(e)}"