import os
# from dotenv import load_dotenv
# load_dotenv()
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
        
        result = supabase.table("chats").upsert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating chat: {e}")
        return None

def get_chats():
    """Get all chat records from Supabase"""
    try:
        result = supabase.table("chats").select("*").execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching chats: {e}")
        return []

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

def create_subscription(
    chat_id: int,
    panel_client_id: str = None,
    url: str = None,
    is_active: bool = True,
    expity_time: float = None,
    email: str = None
):
    """Create a new subscription record in Supabase"""
    try:
        data = {
            "chat_id": chat_id,
            "panel_client_id": panel_client_id,
            "url": url,
            "is_active": is_active,
            "expity_time": expity_time,
            "email": email
        }
        result = supabase.table("subscriptions").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating subscription: {e}")
        return None