import httpx
import json
import uuid
from datetime import datetime
from db import Server
from dataclasses import dataclass
from utils import get_now_ms

@dataclass
class SubscribeInfo:
    id: int
    inboundId: int
    enable: bool
    active: bool
    up: int
    down: int
    expiryTime: int
    total: int
    reset: int
    tgId: int

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


    def _serialize_user(self, obj: dict) -> SubscribeInfo:
        return SubscribeInfo(
            id=obj['id'],
            inboundId=obj['inboundId'],
            enable=obj['enable'],
            up=obj['up'],
            down=obj['down'],
            expiryTime=obj['expiryTime'],
            active=obj['enable'] and (obj['expiryTime'] == 0 or obj['expiryTime'] > get_now_ms()),
            total=obj['total'],
            reset=obj['reset'],
            tgId=int(obj['email'])
        )


    async def get_client_stats(self, telegram_id: int):
        try:
            response = await self.client.get(
                f"{self.base_url}/panel/api/inbounds/getClientTraffics/{telegram_id}",
                cookies=self.cookie
            )
            data = response.json()
            if data.get("success") and data.get("obj"):
                return self._serialize_user(data.get("obj"))
            return None
        except Exception:
            return None
        
    
    async def get_all_clients_expiry(self):
        try:
            response = await self.client.get(
                f"{self.base_url}/panel/api/inbounds/list",
                cookies=self.cookie
            )
            data = response.json()

            if data.get("success") and data.get("obj"):
                return list(map(lambda client: {
                    "uuid": client.get("uuid"),
                    "tgId": client.get("email"),
                    "expiryTime": client.get("expiryTime")
                }, data.get("obj")[0].get("clientStats")))
        except Exception:
            return None


    async def add_client(self, telegram_id: int, limit_gb: int = 0, expiry_days: int = 30):
        uuid_ = str(uuid.uuid4())
        expiry_time = int((datetime.utcnow().timestamp() + (expiry_days * 86400)) * 1000)
        limit_bytes = limit_gb * 1024 * 1024 * 1024 if limit_gb > 0 else 0
        
        client_settings = {
            "id": uuid_,
            "alterId": 0,
            "email": str(telegram_id),
            "limitIp": 0,
            "totalGB": limit_bytes,
            "expiryTime": expiry_time,
            "enable": True,
            "tgId": telegram_id,
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
        
    
    async def extend_client_subscription(self, client_uuid: str, telegram_id: int, sub: SubscribeInfo, add_days: int):
        try:
            if not sub:
                return await self.add_client(telegram_id, 0, add_days)

            now_ms = int(datetime.utcnow().timestamp() * 1000)
  
            base_time = max(sub.expiryTime, now_ms)
            new_expiry = base_time + (add_days * 86400 * 1000)

            client_settings = {
                "id": client_uuid,
                "alterId": 0,
                "email": str(telegram_id),
                "limitIp": 0,
                "totalGB": sub.total,
                "expiryTime": new_expiry,
                "enable": True,
                "tgId": "",
                "subId": ""
            }

            params = {
                "id": self.data["inbound_id"],
                "settings": json.dumps({"clients": [client_settings]})
            }

            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/updateClient/{client_uuid}",
                json=params,
                cookies=self.cookie
            )
            return response.json().get("success", False)
        except Exception:
            return False
        
    
    async def toggle_client_status(self, client_uuid: str, telegram_id: int, sub: SubscribeInfo, enable: bool):
        try:
            client_settings = {
                "id": client_uuid,
                "alterId": 0,
                "email": str(telegram_id),
                "limitIp": 0,
                "totalGB": sub.total,
                "expiryTime": sub.expiryTime,
                "enable": enable,
                "tgId": "",
                "subId": ""
            }

            params = {
                "id": self.data["inbound_id"],
                "settings": json.dumps({"clients": [client_settings]})
            }

            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/updateClient/{client_uuid}",
                json=params,
                cookies=self.cookie
            )

            return response.json().get("success", False)
        except Exception:
            return False


    async def delete_client(self, client_uuid: str):
        try:
            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/{self.data["inbound_id"]}/delClient/{client_uuid}",
                cookies=self.cookie
            )
            return response.json().get("success", False)
        except Exception:
            return False


    async def close(self):
        await self.client.aclose()
