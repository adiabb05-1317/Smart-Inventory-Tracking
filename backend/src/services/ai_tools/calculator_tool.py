from langchain.tools import BaseTool


class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = """Perform mathematical calculations.
    Input should be a mathematical expression like '100 * 50 + 20'
    """
    
    def _run(self, expression: str) -> str:
        try:
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error in calculation: {str(e)}"
