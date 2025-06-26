from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str
    status: str


class TaskCreate(TaskBase):
    agent_id: int


class Task(TaskBase):
    id: int
    agent_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentBase(BaseModel):
    name: str
    description: str


class AgentCreate(AgentBase):
    pass


class Agent(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tasks: List[Task] = []

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    message: str
    agent_id: int = 1  # Default to agent ID 1 for demo


class ChatResponse(BaseModel):
    response: str
    metadata_info: Optional[Dict[str, Any]] = None


class ChatHistory(BaseModel):
    id: int
    agent_id: int
    message: str
    response: str
    created_at: datetime
    metadata_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
