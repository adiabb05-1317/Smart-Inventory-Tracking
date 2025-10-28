import os
from langchain_cerebras import ChatCerebras
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain import hub
from dotenv import load_dotenv
from .ai_tools.sql_executor_tool import SQLExecutorTool
from .ai_tools.calculator_tool import CalculatorTool
from ..db.db_manager import DBManager

# Load environment variables
load_dotenv()


class InventoryAgent:
    def __init__(self, db_manager: DBManager = None):
        cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
        if not cerebras_api_key:
            raise ValueError("CEREBRAS_API_KEY not found in environment variables")
        
        # Initialize database
        if db_manager is None:
            db_manager = DBManager()
            db_manager.initialize_pool()
        
        self.db_manager = db_manager
        
        self.llm = ChatCerebras(
            model="llama3.1-8b",
            api_key=cerebras_api_key,
            temperature=0.1,
            max_tokens=1000
        )
        
        # Initialize tools
        sql_tool = SQLExecutorTool()
        sql_tool.db_manager = self.db_manager
        
        self.tools = [
            sql_tool,
            CalculatorTool()
        ]
        
        # Use ReAct prompt template
        template = """You are an inventory assistant for an electronics store. Answer questions using the available tools.

You have access to these tools:
{tools}

Use this format:

Question: the input question
Thought: think about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the question

Database Schema:
- products: id, name, category, price, stock_quantity, reorder_level, supplier, warranty_months, last_restocked
- sales_history: id, product_id, quantity_sold, sale_price, sale_date

SQL Tips:
- Always include non-aggregated columns in GROUP BY
- Use aggregate functions (SUM, AVG, MAX, MIN, COUNT) for grouped data
- For top sellers: GROUP BY p.id, p.name, p.price, p.stock_quantity

Examples:
Question: How many products do we have?
Thought: I need to count all products
Action: sql_executor
Action Input: SELECT COUNT(*) FROM products
Observation: Result: 150
Thought: I now know the final answer
Final Answer: We have 150 products in our inventory.

Question: Which products are most profitable?
Thought: I need to find products with highest revenue
Action: sql_executor
Action Input: SELECT p.name, SUM(s.quantity_sold * s.sale_price) as revenue FROM products p JOIN sales_history s ON p.id = s.product_id GROUP BY p.id, p.name ORDER BY revenue DESC LIMIT 5
Observation: Found 2 result(s): 1. Samsung Galaxy S24 | 61199.32 2. MacBook Pro 16" | 29999.88
Thought: I now know the final answer
Final Answer: The most profitable products are: 1. Samsung Galaxy S24 with $61,199.32 in revenue, 2. MacBook Pro 16" with $29,999.88 in revenue. I recommend stocking these high-revenue items.

Question: Calculate 100 * 50
Thought: I need to perform a calculation
Action: calculator
Action Input: 100 * 50
Observation: Result: 5000
Thought: I now know the final answer
Final Answer: The result is 5,000.

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        
        self.agent = create_react_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,  # Increased to allow for SQL retries
            handle_parsing_errors=True,
            return_intermediate_steps=False,
            early_stopping_method="generate"  # Generate final answer even if max iterations reached
        )
    
    def chat(self, message: str):
        """Process user message and return AI response"""
        try:
            result = self.executor.invoke({"input": message})
            
            output = result.get("output", "")
            
            # If we have output, return it
            if output and "Agent stopped" not in output:
                return {
                    "output": output,
                    "intermediate_steps": []
                }
            
            # If no output or agent stopped, provide helpful message
            return {
                "output": "I had trouble answering that. Try asking:\n- 'What are the top selling products?'\n- 'How many products do we have?'\n- 'Show me low stock items'\n- 'Calculate restocking cost'",
                "intermediate_steps": []
            }
        except Exception as e:
            error_msg = str(e)
            if "GROUP BY" in error_msg:
                return {
                    "output": "I encountered a database query issue. Please try rephrasing your question more simply.",
                    "intermediate_steps": []
                }
            return {
                "output": f"Error processing request. Please try a different question.",
                "intermediate_steps": []
            }
