import requests
import urllib.parse
from .supabase_client import supabase
import uuid
import json

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

    def add_client(self, email, expiry_time=0, client_id=None):
        """Add a client to inbound ID and return connection string

        Args:
            email (str): Client email identifier
            expiry_time (int): Expiry time in ms
            client_id (str, optional): UUID for the client. If not provided, a new one is generated.

        Returns:
            str: Connection string for the new client
        """
        inbound_id = 1

        url = f"{self.base_url}/panel/inbound/addClient"
        headers = {
            "Cookie": self.cookie,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        if client_id is None:
            client_id = str(uuid.uuid4())
        client_settings = {
            "clients": [{
                "id": client_id,
                "flow": "",
                "email": email,
                "limitIp": 0,
                "totalGB": 0,
                "expiryTime": expiry_time,
                "enable": True,
                "tgId": "",
                "subId": "",
                "reset": 0
            }]
        }

        data = {
            "id": inbound_id,
            "settings": json.dumps(client_settings)
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            return self.get_connection_string(inbound_id, client_id, email)
        elif response.status_code == 401:
            self.cookie = self._login()
            return self.add_client(email, expiry_time, client_id)
        else:
            raise Exception(f"Failed to add client: {response.status_code}")

    def get_connection_string(self, inbound_id, client_id, email):
        """Fetch inbounds and compose connection string for the client."""
        inbounds = self.get_inbounds()
        inbound = None
        for ib in inbounds.get("obj", []):
            if ib.get("id") == inbound_id:
                inbound = ib
                break
        if not inbound:
            raise Exception(f"Inbound {inbound_id} not found")
        settings = json.loads(inbound["settings"])
        client = None
        for c in settings.get("clients", []):
            if c.get("id") == client_id or c.get("email") == email:
                client = c
                break
        if not client:
            raise Exception("Client not found in inbound settings")
        stream_settings = json.loads(inbound["streamSettings"])
        pbk = stream_settings.get("realitySettings", {}).get("settings", {}).get("publicKey", "")
        fp = stream_settings.get("realitySettings", {}).get("settings", {}).get("fingerprint", "")
        sni = stream_settings.get("realitySettings", {}).get("serverNames", [""])[0]
        sid = stream_settings.get("realitySettings", {}).get("shortIds", [""])[0]
        spx = stream_settings.get("realitySettings", {}).get("settings", {}).get("spiderX", "/")
        spx = urllib.parse.quote(spx, safe='')

        host = self.base_url.split("//")[-1].split("/")[0]
        host = host.split(":")[0]
        port = inbound.get("port")
        protocol = inbound.get("protocol")
        remark = inbound.get("remark")
        conn_str = (
            f"{protocol}://{client['id']}@{host}:{port}"
            f"?type=tcp&security=reality"
            f"&pbk={pbk}&fp={fp}&sni={sni}&sid={sid}&spx={spx}"
            f"#{remark}-{email}"
        )
        return conn_str

    def get_client_by_id(self, client_id):
        """
        Retrieve client information by client_id from all inbounds.

        Args:
            client_id (str): The UUID of the client.

        Returns:
            dict: The client object if found, otherwise None.
        """
        inbounds = self.get_inbounds()
        for ib in inbounds.get("obj", []):
            settings = json.loads(ib.get("settings", "{}"))
            for client in settings.get("clients", []):
                if client.get("id") == client_id:
                    return client
        return

    def get_clients(self):
        """
        Retrieve all clients from all inbounds.

        Returns:
            list: A list of all client objects.
        """
        clients = []
        inbounds = self.get_inbounds()
        for ib in inbounds.get("obj", []):
            settings = json.loads(ib.get("settings", "{}"))
            clients.extend(settings.get("clients", []))
        return clients

    def update_client(self, client_id, client_data, inbound_id=1):
        """
        Update a client by client_id.

        Args:
            client_id (str): The UUID of the client.
            client_data (dict): The client data to update (should include all required fields).
                Example:
                {
                    "id": "4fd2b6d5-6a28-455a-8869-3f57e71d58da",
                    "flow": "",
                    "email": "6527907-preshetin",
                    "limitIp": 0,
                    "totalGB": 0,
                    "expiryTime": 1751609375000,
                    "enable": True,
                    "tgId": "",
                    "subId": "",
                    "comment": "",
                    "reset": 0
                }
            inbound_id (int, optional): The inbound ID. Defaults to 1.

        Returns:
            bool: True if update was successful, raises Exception otherwise.
        """
        url = f"{self.base_url}/panel/inbound/updateClient/{client_id}"
        headers = {
            "Cookie": self.cookie,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        client_settings = {
            "clients": [client_data]
        }
        data = {
            "id": inbound_id,
            "settings": json.dumps(client_settings)
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return True
        elif response.status_code == 401:
            self.cookie = self._login()
            return self.update_client(client_id, client_data, inbound_id)
        else:
            raise Exception(f"Failed to update client: {response.status_code} {response.text}")

    def get_first_client_by_chat_id(self, chat_id):
        """
        Retrieve the first client whose email starts with the given chat_id followed by a dash.

        Args:
            chat_id (str or int): The chat id to search for.

        Returns:
            dict: The client object if found, otherwise None.
        """
        chat_id_str = str(chat_id)
        clients = self.get_clients()
        for client in clients:
            email = client.get('email', '')
            if email.startswith(f"{chat_id_str}-"):
                return client
        return None