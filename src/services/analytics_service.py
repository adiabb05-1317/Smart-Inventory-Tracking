from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal


class AnalyticsService:
    """Business logic layer for analytics and forecasting."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def calculate_sales_trends(self, period_days: int) -> Dict[str, Any]:
        """Calculate sales trends for specified period."""
        query = """
            SELECT 
                p.id,
                p.name,
                p.category,
                COALESCE(SUM(s.quantity_sold), 0) as total_units,
                COALESCE(SUM(s.quantity_sold * s.sale_price), 0) as total_revenue
            FROM products p
            LEFT JOIN sales_history s ON p.id = s.product_id
                AND s.sale_date >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY p.id, p.name, p.category
            HAVING SUM(s.quantity_sold) > 0
            ORDER BY total_revenue DESC
        """
        
        results = self.db_manager.fetch_all(query, (period_days,))
        
        total_revenue = Decimal('0')
        total_units = 0
        top_products = []
        
        for row in results:
            product_id, name, category, units, revenue = row
            total_units += int(units)
            total_revenue += Decimal(str(revenue))
            
            top_products.append({
                "product_id": product_id,
                "name": name,
                "category": category,
                "units_sold": int(units),
                "revenue": float(revenue)
            })
        
        # Calculate category breakdown
        category_query = """
            SELECT 
                p.category,
                COALESCE(SUM(s.quantity_sold), 0) as total_units,
                COALESCE(SUM(s.quantity_sold * s.sale_price), 0) as total_revenue
            FROM products p
            LEFT JOIN sales_history s ON p.id = s.product_id
                AND s.sale_date >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY p.category
            HAVING SUM(s.quantity_sold) > 0
            ORDER BY total_revenue DESC
        """
        
        category_results = self.db_manager.fetch_all(category_query, (period_days,))
        
        categories = []
        for row in category_results:
            category, units, revenue = row
            categories.append({
                "category": category,
                "units_sold": int(units),
                "revenue": float(revenue)
            })
        
        return {
            "period": f"{period_days}d",
            "total_revenue": float(total_revenue),
            "total_units": total_units,
            "top_products": top_products,
            "categories": categories
        }
    
    def forecast_demand(self, product_id: int) -> Dict[str, Any]:
        """Forecast demand using simple moving average."""
        # Get product info
        product_query = """
            SELECT id, name, stock_quantity, reorder_level
            FROM products
            WHERE id = %s
        """
        product = self.db_manager.fetch_one(product_query, (product_id,))
        
        if not product:
            raise ValueError(f"Product with id {product_id} not found")
        
        product_name = product[1]
        current_stock = product[2]
        reorder_level = product[3]
        
        # Calculate average daily sales for last 7 days
        sales_query = """
            SELECT COALESCE(SUM(quantity_sold), 0) as total_sold
            FROM sales_history
            WHERE product_id = %s
                AND sale_date >= CURRENT_TIMESTAMP - INTERVAL '7 days'
        """
        sales_result = self.db_manager.fetch_one(sales_query, (product_id,))
        total_sold_7d = int(sales_result[0]) if sales_result else 0
        
        avg_daily_sales = total_sold_7d / 7.0
        
        # Calculate estimated days until stockout
        if avg_daily_sales > 0:
            estimated_days_until_stockout = current_stock / avg_daily_sales
        else:
            estimated_days_until_stockout = float('inf')
        
        # Calculate recommended reorder quantity
        # Strategy: ensure 14 days of stock based on average daily sales
        target_stock_days = 14
        target_stock = avg_daily_sales * target_stock_days
        
        if current_stock < reorder_level:
            recommended_reorder_quantity = max(
                int(target_stock - current_stock),
                reorder_level
            )
        else:
            recommended_reorder_quantity = 0
        
        return {
            "product_id": product_id,
            "product_name": product_name,
            "current_stock": current_stock,
            "reorder_level": reorder_level,
            "avg_daily_sales": round(avg_daily_sales, 2),
            "estimated_days_until_stockout": round(estimated_days_until_stockout, 1) 
                if estimated_days_until_stockout != float('inf') else None,
            "recommended_reorder_quantity": recommended_reorder_quantity,
            "forecast_period": "7 days moving average"
        }
    
    def calculate_inventory_turnover(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Calculate inventory turnover ratio."""
        # Build query based on category filter
        where_clause = "WHERE p.category = %s" if category else ""
        params = (category,) if category else None
        
        query = f"""
            SELECT 
                p.id,
                p.name,
                p.category,
                p.stock_quantity,
                COALESCE(SUM(s.quantity_sold), 0) as total_sold
            FROM products p
            LEFT JOIN sales_history s ON p.id = s.product_id
                AND s.sale_date >= CURRENT_TIMESTAMP - INTERVAL '30 days'
            {where_clause}
            GROUP BY p.id, p.name, p.category, p.stock_quantity
        """
        
        results = self.db_manager.fetch_all(query, params)
        
        slow_moving_products = []
        total_turnover = 0
        product_count = 0
        
        for row in results:
            product_id, name, prod_category, current_stock, total_sold = row
            
            # Calculate turnover ratio: units sold / average inventory
            # Average inventory approximated as current_stock (simplified)
            if current_stock > 0:
                turnover_ratio = float(total_sold) / float(current_stock)
            else:
                turnover_ratio = float(total_sold) if total_sold > 0 else 0
            
            total_turnover += turnover_ratio
            product_count += 1
            
            # Identify slow-moving items (turnover < 1.0)
            if turnover_ratio < 1.0:
                slow_moving_products.append({
                    "product_id": product_id,
                    "name": name,
                    "category": prod_category,
                    "current_stock": current_stock,
                    "units_sold_30d": int(total_sold),
                    "turnover_ratio": round(turnover_ratio, 2)
                })
        
        avg_turnover = total_turnover / product_count if product_count > 0 else 0
        
        return {
            "category": category if category else "All",
            "period": "30 days",
            "average_turnover_ratio": round(avg_turnover, 2),
            "slow_moving_products": sorted(
                slow_moving_products, 
                key=lambda x: x["turnover_ratio"]
            )
        }
    
    def get_top_performers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing products by revenue."""
        query = """
            SELECT 
                p.id,
                p.name,
                p.category,
                p.stock_quantity,
                SUM(s.quantity_sold) as total_units,
                SUM(s.quantity_sold * s.sale_price) as total_revenue
            FROM products p
            INNER JOIN sales_history s ON p.id = s.product_id
            WHERE s.sale_date >= CURRENT_TIMESTAMP - INTERVAL '30 days'
            GROUP BY p.id, p.name, p.category, p.stock_quantity
            ORDER BY total_revenue DESC
            LIMIT %s
        """
        
        results = self.db_manager.fetch_all(query, (limit,))
        
        top_performers = []
        for row in results:
            product_id, name, category, stock, units, revenue = row
            top_performers.append({
                "product_id": product_id,
                "product_name": name,
                "category": category,
                "units_sold": int(units),
                "revenue": float(revenue),
                "stock_remaining": stock
            })
        
        return top_performers
    
    def get_restock_urgency(self) -> List[Dict[str, Any]]:
        """Calculate restock urgency for low-stock products."""
        # Get low stock products
        query = """
            SELECT 
                p.id,
                p.name,
                p.category,
                p.stock_quantity,
                p.reorder_level,
                COALESCE(SUM(s.quantity_sold), 0) as total_sold_7d
            FROM products p
            LEFT JOIN sales_history s ON p.id = s.product_id
                AND s.sale_date >= CURRENT_TIMESTAMP - INTERVAL '7 days'
            WHERE p.stock_quantity < p.reorder_level
            GROUP BY p.id, p.name, p.category, p.stock_quantity, p.reorder_level
        """
        
        results = self.db_manager.fetch_all(query)
        
        urgency_list = []
        
        for row in results:
            product_id, name, category, current_stock, reorder_level, total_sold = row
            
            avg_daily_sales = float(total_sold) / 7.0
            
            # Calculate urgency score
            stock_deficit = reorder_level - current_stock
            
            if avg_daily_sales > 0:
                urgency_score = stock_deficit / avg_daily_sales
                days_until_stockout = current_stock / avg_daily_sales
            else:
                urgency_score = stock_deficit
                days_until_stockout = None
            
            # Determine action level
            if current_stock == 0 or (days_until_stockout and days_until_stockout < 2):
                action = "CRITICAL"
            elif current_stock < reorder_level * 0.5 or (days_until_stockout and days_until_stockout < 5):
                action = "HIGH"
            else:
                action = "MEDIUM"
            
            urgency_list.append({
                "product_id": product_id,
                "product_name": name,
                "category": category,
                "current_stock": current_stock,
                "reorder_level": reorder_level,
                "avg_daily_sales": round(avg_daily_sales, 2),
                "days_until_stockout": round(days_until_stockout, 1) if days_until_stockout else None,
                "urgency_score": round(urgency_score, 2),
                "action": action
            })
        
        # Sort by urgency score descending (higher score = more urgent)
        urgency_list.sort(key=lambda x: x["urgency_score"], reverse=True)
        
        return urgency_list

