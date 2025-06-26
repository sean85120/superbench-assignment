from fastapi import APIRouter

from backend.src.utils.ai_agent import AIAgent

router = APIRouter(prefix="/agent", tags=["agent"])

# Initialize AI Agent
ai_agent = AIAgent()


@router.post("/pricing/")
async def update_pricing_context(pricing_data: dict):
    ai_agent.set_pricing_context(pricing_data)
    return {"message": "Pricing context updated successfully"}
