from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel
from typing import Optional

@dataclass
class ChatConversation:
    id: int
    user_id: int
    last_message_at: Optional[datetime]
    created_at: datetime


@dataclass
class ChatMessage:
    id: int
    conversation_id: int
    sender_type: str
    message: str
    message_metadata: Optional[Dict]
    created_at: datetime



class ChatRequest(BaseModel):
    prompt: str
    user_id: int
    chat_id: Optional[int] = None
