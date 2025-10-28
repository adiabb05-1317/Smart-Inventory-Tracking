import os
from langchain_cerebras import ChatCerebras
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from .ai_tools.inventory_query_tool import InventoryQueryTool
from .ai_tools.sales_analyzer_tool import SalesAnalyzerTool
from .ai_tools.restock_advisor_tool import RestockAdvisorTool
from .ai_tools.calculator_tool import CalculatorTool
from .product_service import ProductService
from .analytics_service import AnalyticsService
from ..db.db_manager import DBManager

# Load environment variables
load_dotenv()


class InventoryAgent:
    def __init__(self, db_manager: DBManager = None):
        cerebras_api_key = os.getenv("CEREBRAS_API_KEY")

        # Initialize services
        if db_manager is None:
            db_manager = DBManager()
            db_manager.initialize_pool()

        self.product_service = ProductService(db_manager)
        self.analytics_service = AnalyticsService(db_manager)

        # Use mock LLM if no API key is provided
        if not cerebras_api_key or cerebras_api_key == "dummy_key_for_testing":
            self.use_mock = True
            self.llm = None
        else:
            self.use_mock = False
            self.llm = ChatCerebras(
                model="llama3.1-8b",
                api_key=cerebras_api_key,
                temperature=0.7,
                max_tokens=1000
            )
        
        # Initialize tools with services
        inventory_tool = InventoryQueryTool(self.product_service)
        sales_tool = SalesAnalyzerTool(self.analytics_service)
        restock_tool = RestockAdvisorTool(self.analytics_service)
        
        self.tools = [
            inventory_tool,
            sales_tool,
            restock_tool,
            CalculatorTool()
        ]
        
        if not self.use_mock:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an intelligent inventory management assistant.
                You help users manage their electronics store inventory by:
                - Answering questions about products and stock levels
                - Analyzing sales trends and patterns
                - Providing restock recommendations
                - Performing calculations

                Always be helpful, concise, and data-driven."""),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])

            self.agent = create_tool_calling_agent(self.llm, self.tools, prompt)
            self.executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                max_iterations=3
            )
        else:
            self.agent = None
            self.executor = None
    
    def chat(self, message: str):
        if self.use_mock:
            # Mock response for testing without API key
            if "low stock" in message.lower():
                try:
                    # Use the inventory tool directly
                    result = self.tools[0]._run("low stock items")  # inventory_tool
                    return {"output": f"📦 **Low Stock Alert**\n\n{result}\n\n💡 **Recommendation:** Consider restocking these items to avoid stockouts.", "intermediate_steps": []}
                except Exception as e:
                    return {"output": f"⚠️ I encountered an error checking low stock items: {str(e)}", "intermediate_steps": []}
            elif "sales" in message.lower() or "trends" in message.lower():
                try:
                    # Use the sales tool directly
                    result = self.tools[1]._run("trends:30d")  # sales_tool
                    return {"output": f"📈 **Sales Analysis**\n\n{result}\n\n💡 **Tip:** Monitor these trends to optimize your inventory levels.", "intermediate_steps": []}
                except Exception as e:
                    return {"output": f"⚠️ I encountered an error analyzing sales: {str(e)}", "intermediate_steps": []}
            elif "restock" in message.lower():
                try:
                    # Use the restock tool directly
                    result = self.tools[2]._run("get recommendations")  # restock_tool
                    return {"output": f"🚨 **Restock Recommendations**\n\n{result}\n\n💡 **Action Items:**\n• Review items marked as CRITICAL immediately\n• Plan orders for HIGH priority items within 1-2 days\n• Monitor MEDIUM priority items regularly", "intermediate_steps": []}
                except Exception as e:
                    return {"output": f"⚠️ I encountered an error getting restock recommendations: {str(e)}", "intermediate_steps": []}
            else:
                return {"output": "🤖 **Smart Inventory Assistant**\n\nI can help you with:\n\n📦 **Inventory Management**\n• Check low stock items\n• View product details\n• Search by category\n\n📊 **Sales Analytics**\n• Analyze sales trends\n• Identify top performers\n• Review category performance\n\n🚨 **Restock Planning**\n• Get restock recommendations\n• Check urgency levels\n• Plan inventory orders\n\n🧮 **Calculations**\n• Perform mathematical operations\n\n💬 **Try asking:**\n• \"Show me low stock items\"\n• \"What are my top performers?\"\n• \"Sales trends for last 30 days\"\n• \"What needs restocking urgently?\"", "intermediate_steps": []}
        else:
            result = self.executor.invoke({"input": message})
            return result
