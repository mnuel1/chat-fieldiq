from datetime import datetime
from typing import List, Optional, Dict
from config.config import get_supabase_client

class Chat:
    def __init__(self):
        self.client = get_supabase_client()

    def create_conversation(self, user_id: int) -> Dict:        
        response = self.client.table("chat_conversations").insert({
            "user_id": user_id,            
        }).execute()
        
        # return the id
        return response.data[0]["id"] if response.data[0] else None

    def add_message(self, conversation_id: int, sender_type: str, message: str, metadata: Optional[Dict] = None) -> Dict:
        now = datetime.now(datetime.timezone.utc)

        message_data = {
            "conversation_id": conversation_id,
            "sender_type": sender_type,
            "message": message,
            "message_metadata": metadata or {},            
        }

        insert_resp = self.client.table("chat_messages").insert(message_data).execute()

        self.client.table("chat_conversation").update({
            "last_message_at": now
        }).eq("id", conversation_id).execute()

        return insert_resp.data[0] if insert_resp.data else None

    def get_conversation_messages(self, conversation_id: int) -> List[Dict]:
        response = self.client.table("chat_messages")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("created_at", desc=False)\
            .execute()
        return response.data or []
