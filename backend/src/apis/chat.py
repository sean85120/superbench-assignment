from typing import List

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.db.database import get_db
from backend.src.models.models import Agent
from backend.src.models.models import ChatHistory as ChatHistoryModel
from backend.src.schemas.schemas import ChatHistory, ChatMessage, ChatResponse
from backend.src.utils.ai_agent import AIAgent

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize AI Agent
ai_agent = AIAgent()


@router.post("/", response_model=ChatResponse)
async def chat(message: ChatMessage, db: AsyncSession = Depends(get_db)):
    # For demo purposes, we'll use a default agent (ID 1)
    agent = await db.scalar(select(Agent).where(Agent.id == message.agent_id))

    if not agent:
        # Create default agent if it doesn't exist
        agent = Agent(
            id=1,
            name="BikeHero Assistant",
            description="AI assistant for bike maintenance services",
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)

    # Process message with AI agent
    response = await ai_agent.process_message(message.message)

    logger.info(f"Message: {message}")
    logger.info(f"Response: {response}")

    # Save chat history using the SQLAlchemy model
    chat_history = ChatHistoryModel(
        agent_id=message.agent_id,
        message=message.message,
        response=response["response"],
        metadata_info=response["metadata_info"],
    )
    db.add(chat_history)
    await db.commit()

    return response


@router.get("/history/", response_model=List[ChatHistory])
async def get_chat_history(db: AsyncSession = Depends(get_db)):
    """Get all chat history for demo purposes"""
    result = await db.execute(
        select(ChatHistoryModel).order_by(ChatHistoryModel.created_at.desc())
    )
    return result.scalars().all()
