from langchain.tools import BaseTool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..analytics_service import AnalyticsService


class RestockAdvisorTool(BaseTool):
    name: str = "restock_advisor"
    description: str = """Get restock recommendations with urgency levels.
    Use this to find which products need restocking urgently.
    Input: 'get recommendations'
    """

    def __init__(self, analytics_service):
        super().__init__()
        self._analytics_service = analytics_service
    
    def _run(self, query: str) -> str:
        try:
            urgency_list = self._analytics_service.get_restock_urgency()
            
            if not urgency_list:
                return "No urgent restock recommendations. All products are adequately stocked."
            
            result = f"Restock Recommendations ({len(urgency_list)} items):\n\n"
            
            for item in urgency_list[:5]:
                result += f"- {item['product_name']} ({item['category']})\n"
                result += f"  Action: {item['action']}\n"
                result += f"  Current Stock: {item['current_stock']} (Reorder at: {item['reorder_level']})\n"
                result += f"  Avg Daily Sales: {item['avg_daily_sales']}\n"
                
                if item['days_until_stockout']:
                    result += f"  Days Until Stockout: {item['days_until_stockout']}\n"
                
                result += "\n"
            
            if len(urgency_list) > 5:
                result += f"...and {len(urgency_list) - 5} more items need attention"
            
            return result
        
        except Exception as e:
            return f"Error getting restock advice: {str(e)}"
