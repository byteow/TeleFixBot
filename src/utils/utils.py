from datetime import datetime, timezone
from config import BOT_USERNAME

def get_utc_time(datetime: datetime):
    return datetime.strftime("%d %b %Y, %H:%M UTC")

def ms_to_datetime(ms: int):
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return dt.strftime("%H:%M %d.%m.%Y UTC")

def generate_vless_link(server_data: dict, uuid: str):
    host = server_data['host']
    port = 443
    
    params = {
        "encryption": "none",
        "security": "reality",
        "sni": server_data['sni'],
        "fp": "chrome",     
        "pbk": server_data['pbk'],
        "sid": server_data['sid'],
        "type": "tcp",      
        "flow": "xtls-rprx-vision"
    }

    params_str = "&".join([f"{k}={v}" for k, v in params.items() if v])
    remark = "TeleFix" 
    
    return f"vless://{uuid}@{host}:{port}?{params_str}#{remark}"

def generate_referral_link(telegram_id: int):
    return f"https://t.me/{BOT_USERNAME}?start=referral_{telegram_id}"

def bytes_to_gb(b):
    return round(b / (1024**3), 2)

def get_now_ms():
    return int(datetime.utcnow().timestamp() * 1000)