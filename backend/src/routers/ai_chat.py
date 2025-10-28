from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from ..services.ai_agent import InventoryAgent

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

# Initialize agent lazily
_agent = None


def get_agent(req: Request):
    """Get or create AI agent instance"""
    global _agent
    if _agent is None:
        db_manager = req.app.state.db_manager
        _agent = InventoryAgent(db_manager)
    return _agent


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    tools_used: list = []


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """Chat with AI inventory assistant"""
    try:
        agent = get_agent(req)
        result = agent.chat(request.message)
        return ChatResponse(
            response=result.get("output", ""),
            tools_used=result.get("intermediate_steps", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Check AI agent health"""
    return {"status": "healthy", "model": "llama3.1-8b"}
