from langchain.tools import BaseTool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..analytics_service import AnalyticsService


class SalesAnalyzerTool(BaseTool):
    name: str = "sales_analyzer"
    description: str = """Analyze sales data and trends. Use this to get:
    - Sales trends (7d, 30d, 90d periods)
    - Top performing products
    Input should be like 'trends:30d' or 'top performers:10'
    """

    def __init__(self, analytics_service):
        super().__init__()
        self._analytics_service = analytics_service
    
    def _run(self, query: str) -> str:
        try:
            if "trends:" in query.lower():
                period = query.split("trends:")[1].strip()
                period_days = int(period.replace('d', ''))
                
                trends = self._analytics_service.calculate_sales_trends(period_days)
                
                result = f"Sales Trends for last {period_days} days:\n"
                result += f"Total Revenue: ${trends['total_revenue']:,.2f}\n"
                result += f"Total Units Sold: {trends['total_units']}\n\n"
                
                if trends['top_products']:
                    result += "Top Products:\n"
                    for p in trends['top_products'][:5]:
                        result += f"- {p['name']}: {p['units_sold']} units, ${p['revenue']:,.2f}\n"
                
                return result
                
            elif "top performers" in query.lower():
                limit = 5
                if ":" in query:
                    limit = int(query.split(":")[1].strip())
                
                top = self._analytics_service.get_top_performers(limit)
                
                if not top:
                    return "No sales data available for top performers."
                
                result = f"Top {len(top)} Performers (last 30 days):\n"
                for idx, p in enumerate(top, 1):
                    result += f"{idx}. {p['product_name']}: {p['units_sold']} units, ${p['revenue']:,.2f}\n"
                
                return result
            else:
                return "Please specify 'trends:period' (e.g., 'trends:30d') or 'top performers:limit' (e.g., 'top performers:5')"
        
        except Exception as e:
            return f"Error analyzing sales: {str(e)}"
