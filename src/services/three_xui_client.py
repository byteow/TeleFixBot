import httpx
import json
from datetime import datetime

class ThreeXUIClient:
    def __init__(self, host: str, port: int, login: str, password: str):
        self.base_url = f"http://{host}:{port}"
        self.login_data = {"username": login, "password": password}
        self.client = httpx.AsyncClient(timeout=10.0)
        self.cookie = None


    async def login(self) -> bool:
        try:
            response = await self.client.post(f"{self.base_url}/login", data=self.login_data)
            if response.status_code == 200:
                self.cookie = response.cookies
                return True
            return False
        except Exception:
            return False


    async def get_client_stats(self, uuid: str):
        try:
            response = await self.client.get(
                f"{self.base_url}/panel/api/inbounds/getClientTraffics/{uuid}",
                cookies=self.cookie
            )
            data = response.json()
            if data.get("success") and data.get("obj"):
                return data.get("obj")
            return None
        except Exception:
            return None


    async def add_client(self, inbound_id: int, uuid: str, limit_gb: int = 0, expiry_days: int = 30):
        expiry_time = int((datetime.utcnow().timestamp() + (expiry_days * 86400)) * 1000)
        limit_bytes = limit_gb * 1024 * 1024 * 1024 if limit_gb > 0 else 0
        
        client_settings = {
            "id": uuid,
            "alterId": 0,
            "email": uuid,
            "limitIp": 0,
            "totalGB": limit_bytes,
            "expiryTime": expiry_time,
            "enable": True,
            "tgId": "",
            "subId": ""
        }
        
        params = {
            "id": inbound_id,
            "settings": json.dumps({"clients": [client_settings]})
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/addClient",
                json=params,
                cookies=self.cookie
            )
            return response.json().get("success", False)
        except Exception:
            return False


    async def delete_client(self, inbound_id: int, uuid: str):
        try:
            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/{inbound_id}/delClient/{uuid}",
                cookies=self.cookie
            )
            return response.json().get("success", False)
        except Exception:
            return False


    async def close(self):
        await self.client.aclose()
