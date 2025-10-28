from langchain.tools import BaseTool
import ast
import operator
from typing import ClassVar, Dict, Type, Callable


class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = """Perform mathematical calculations.
    Input should be a mathematical expression like '100 * 50 + 20' or '1500 / 30'
    Supports: +, -, *, /, **, (), decimals
    """
    
    # Safe operators - marked as ClassVar to avoid Pydantic field error
    operators: ClassVar[Dict[Type, Callable]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }
    
    def _eval_expr(self, node):
        """Safely evaluate mathematical expression"""
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._eval_expr(node.left)
            right = self._eval_expr(node.right)
            return self.operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_expr(node.operand)
            return self.operators[type(node.op)](operand)
        else:
            raise ValueError("Unsupported operation")
    
    def _run(self, expression: str) -> str:
        try:
            # Parse and evaluate safely
            node = ast.parse(expression, mode='eval')
            result = self._eval_expr(node.body)
            return f"Result: {result:,.2f}" if isinstance(result, float) else f"Result: {result}"
        except Exception as e:
            return f"Error: Only basic mathematical operations are allowed (+, -, *, /, **)"
