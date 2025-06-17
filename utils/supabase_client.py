import os
from supabase import create_client, Client

# Initialize Supabase client
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def create_chat(chat_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """Create a new chat record in Supabase"""
    try:
        data = {
            "id": chat_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        }
        
        result = supabase.table("chats").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating chat: {e}")
        return None

def add_message(chat_id: int, is_bot: bool, text: str, update_obj: dict = None):
    """Add a message record to Supabase"""
    try:
        data = {
            "chat_id": chat_id,
            "is_bot": is_bot,
            "text": text,
            "update_obj": update_obj
        }
        
        result = supabase.table("messages").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error adding message: {e}")
        return None