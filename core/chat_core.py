from typing import List, Optional, Dict
from config.config import get_supabase_client


class Chat:
    def __init__(self):
        self.client = get_supabase_client()

    def create_conversation(self, user_id: int) -> int:        
        existing = (
            self.client.table("chat_conversations")
            .select("id")
            .eq("user_profile_id", user_id)
            .limit(1)
            .execute()
        )

        if existing.data and len(existing.data) > 0:
            return existing.data[0]["id"]

        # If not, create a new conversation
        response = (
            self.client.table("chat_conversations")
            .insert({"user_profile_id": user_id})
            .execute()
        )

        return response.data[0]["id"] if response.data else None

    def update_conversation(self, conversation_id: int, form_data):
        self.client.table("chat_conversations").update({
            "form_data": form_data,
            "last_message_at": "now()",
        }).eq("id", conversation_id).execute()

    def add_message(self, conversation_id: int, role: str, message: str, metadata: Optional[Dict] = None) -> Dict:

        message_data = {
            "conversation_id": conversation_id,
            "role": role,
            "message": message,
            "message_metadata": metadata or {},
        }

        insert_resp = self.client.table(
            "chat_messages").insert(message_data).execute()

        return insert_resp.data[0] if insert_resp.data else None

    def get_conversation_messages(self, conversation_id: int) -> List[Dict]:
        response = self.client.table("chat_messages")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("created_at", desc=False)\
            .execute()
        return response.data or []

    def get_recent_messages(self, conversation_id: int, max_messages=6) -> List[Dict]:
        response = (
            self.client
            .table("chat_messages")
            .select("role, message")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .limit(max_messages)
            .execute()
        )

        raw_messages = response.data or []

        formatted_messages = [
            {
                "role": "assistant" if msg["role"] == "model" else "user",
                "content": msg["message"]
            }
            for msg in raw_messages
            if msg["role"] in ("user", "model") and msg["message"]
        ]

        return formatted_messages
    
    def get_conversations_record(self, convo_id: int):
        convo = self.client.table("chat_conversations").select(
            "*").eq("id", convo_id).single().execute()
        print("Convo:", convo.data)
        if convo.data:
            return convo.data
        return None