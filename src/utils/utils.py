from datetime import datetime
from config import MANAGER_TG_USERNAME

def get_utc_time(datetime: datetime):
    return datetime.strftime("%d %b %Y, %H:%M UTC")

def get_manager_link():
    return f"https://t.me/{MANAGER_TG_USERNAME}"