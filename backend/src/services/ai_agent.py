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
            model="gpt-oss-120b",
            api_key=cerebras_api_key,
            temperature=0,
            max_tokens=500
        )
        
        # Initialize tools
        sql_tool = SQLExecutorTool()
        sql_tool.db_manager = self.db_manager
        
        self.tools = [
            sql_tool,
            CalculatorTool()
        ]
        
        # Simplified ReAct prompt with strict formatting to avoid parsing errors
        template = """You are an inventory management assistant. Answer questions using the available tools.

Available tools:
{tools}

Tool names: {tool_names}

STRICT FORMAT - You MUST follow this exactly:

Question: the input question
Thought: think about what to do
Action: tool_name
Action Input: tool input
Observation: result from tool
Thought: I now know the final answer
Final Answer: the answer

RULES:
1. Every "Thought:" MUST be followed by either "Action:" or "Final Answer:"
2. Never include extra text after "Observation:"
3. Use exact tool names: {tool_names}
4. Keep responses concise

Database Tables:
- products: id, name, category, price, stock_quantity, reorder_level, supplier
- sales_history: id, product_id, quantity_sold, sale_price, sale_date

Common Queries:
1. Low stock: SELECT name, stock_quantity FROM products WHERE stock_quantity < reorder_level
2. Product count: SELECT COUNT(*) FROM products
3. Top sellers: SELECT p.name, SUM(s.quantity_sold) as total FROM products p JOIN sales_history s ON p.id = s.product_id GROUP BY p.id, p.name ORDER BY total DESC LIMIT 5

Examples:

Question: What items are low in stock?
Thought: I need to find products where stock is below reorder level
Action: sql_executor
Action Input: SELECT name, stock_quantity FROM products WHERE stock_quantity < reorder_level
Observation: Found 2 result(s):
1. Samsung Galaxy S24 | 8
2. Sony WH-1000XM5 | 5
Thought: I now know the final answer
Final Answer: These items are low in stock: Samsung Galaxy S24 (8 units) and Sony WH-1000XM5 (5 units).

Question: Calculate 100 times 50
Thought: I need to multiply two numbers
Action: calculator
Action Input: 100 * 50
Observation: Result: 5000
Thought: I now know the final answer
Final Answer: 100 times 50 equals 5,000.

Begin!

Question: {input}
{agent_scratchpad}"""

        # Inject tool names so the prompt renders correctly
        tool_names = ", ".join([t.name for t in self.tools])
        prompt = PromptTemplate.from_template(template).partial(tool_names=tool_names)

        self.agent = create_react_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors="Check your output and make sure it follows the format: Thought: [your thought] Action: [tool name] Action Input: [input]",
            max_iterations=5,
            early_stopping_method="force",
            return_intermediate_steps=True
        )
    
    def chat(self, message: str):
        """Process user message and return AI response"""
        try:
            result = self.executor.invoke({"input": message})

            # Extract output and tools used
            output = result.get("output", "")
            steps = result.get("intermediate_steps", [])

            tools_used = []
            for step in steps:
                try:
                    # step structure: (AgentAction, observation)
                    action = step[0]
                    if hasattr(action, "tool") and action.tool:
                        tools_used.append(action.tool)
                except Exception:
                    pass

            # If output indicates a stop or parsing issue, try to recover from last observation
            if output:
                lower = output.lower()
                if ("agent stopped" in lower) or ("parsing" in lower) or ("invalid format" in lower):
                    if steps:
                        last_obs = steps[-1][1] if len(steps[-1]) > 1 else ""
                        if last_obs:
                            return {
                                "output": f"Based on the data: {last_obs}",
                                "intermediate_steps": tools_used
                            }

                return {
                    "output": output,
                    "intermediate_steps": tools_used
                }

            # Fallback if no output
            return {
                "output": "I couldn't process that question. Try asking:\n- 'What items are low in stock?'\n- 'How many products do we have?'\n- 'What are the top selling products?'",
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