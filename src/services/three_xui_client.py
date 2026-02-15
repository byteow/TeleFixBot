import httpx
import json
import uuid
from datetime import datetime
from db import Server
from dataclasses import dataclass

@dataclass
class SubscribeInfo:
    id: int
    inboundId: int
    enable: bool
    email: str
    up: int
    down: int
    expiryTime: int
    total: int
    reset: int

class ThreeXUIClient:
    def __init__(
            self, 
            inbound_id: int, 
            server_id: int, 
            host: str, 
            port: int, 
            login: str,
            password: str,
            sni: str,
            sid: str,
            pbk: str,
            model: Server
        ):
        self.base_url = f"http://{host}:{port}"
        self.login_data = {"username": login, "password": password}
        self.client = httpx.AsyncClient(timeout=10.0)
        self.cookie = None
        self.data = {
            "host": host,
            "port": port,
            "inbound_id": inbound_id,
            "server_id": server_id,
            "sni": sni,
            "sid": sid,
            "pbk": pbk
        }
        self.model = model


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
                obj = data.get("obj")
                return SubscribeInfo(
                    id=obj['id'],
                    inboundId=obj['inboundId'],
                    enable=obj['enable'],
                    email=obj['email'],
                    up=obj['up'],
                    down=obj['down'],
                    expiryTime=obj['expiryTime'],
                    total=obj['total'],
                    reset=obj['reset']
                )
            return None
        except Exception:
            return None


    async def add_client(self, limit_gb: int = 0, expiry_days: int = 30):
        uuid_ = str(uuid.uuid4())
        expiry_time = int((datetime.utcnow().timestamp() + (expiry_days * 86400)) * 1000)
        limit_bytes = limit_gb * 1024 * 1024 * 1024 if limit_gb > 0 else 0
        
        client_settings = {
            "id": uuid_,
            "alterId": 0,
            "email": uuid_,
            "limitIp": 0,
            "totalGB": limit_bytes,
            "expiryTime": expiry_time,
            "enable": True,
            "tgId": "",
            "subId": ""
        }
        
        params = {
            "id": self.data["inbound_id"],
            "settings": json.dumps({"clients": [client_settings]})
        }
        
        try:
            await self.client.post(
                f"{self.base_url}/panel/api/inbounds/addClient",
                json=params,
                cookies=self.cookie
            )
            return uuid_
        except Exception:
            return None


    async def delete_client(self, uuid: str):
        try:
            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/{self.data["inbound_id"]}/delClient/{uuid}",
                cookies=self.cookie
            )
            return response.json().get("success", False)
        except Exception:
            return False


    async def close(self):
        await self.client.aclose()
