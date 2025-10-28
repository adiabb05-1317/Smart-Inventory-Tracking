from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from ..services.ai_agent import InventoryAgent

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

# Initialize agent lazily
agent = None

def get_agent(db_manager):
    global agent
    if agent is None:
        agent = InventoryAgent(db_manager)
    return agent


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    tools_used: list = []


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """Chat with AI inventory assistant"""
    try:
        agent_instance = get_agent(req.app.state.db_manager)
        result = agent_instance.chat(request.message)
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
