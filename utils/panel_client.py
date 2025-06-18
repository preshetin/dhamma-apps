import requests
from .supabase_client import supabase

class PanelClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.cookie = self._get_stored_cookie() or self._login()

    def _get_stored_cookie(self):
        """Get stored cookie from Supabase settings"""
        result = supabase.table("settings").select("value").eq("key", "panel_cookie").execute()
        return result.data[0]["value"] if result.data else None

    def _store_cookie(self, cookie):
        """Store cookie in Supabase settings"""
        supabase.table("settings").upsert({"key": "panel_cookie", "value": cookie}).execute()

    def _login(self):
        """Login to panel and get cookie"""
        login_url = f"{self.base_url}/login"
        data = {
            "username": self.username,
            "password": self.password
        }
        response = requests.post(login_url, data=data)
        
        if response.status_code == 200:
            cookie = response.cookies.get_dict()
            cookie_str = '; '.join([f"{k}={v}" for k, v in cookie.items()])
            self._store_cookie(cookie_str)
            return cookie_str
        raise Exception("Login failed")

    def get_inbounds(self):
        """Get list of inbounds"""
        url = f"{self.base_url}/panel/api/inbounds/list"
        headers = {"Cookie": self.cookie}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            # If unauthorized, try to login again
            self.cookie = self._login()
            return self.get_inbounds()
        else:
            raise Exception(f"Failed to get inbounds: {response.status_code}")