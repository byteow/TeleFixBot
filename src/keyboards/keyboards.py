from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from config import ADMIN_USERNAME

back_button = InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main")

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🚀 ПОДКЛЮЧИТЬ УСКОРЕНИЕ", callback_data="get_link"))
    kb.row(
        InlineKeyboardButton(text="ℹ️ Мой статус", callback_data="about_subscribe"),
        InlineKeyboardButton(text="📥 Софт", callback_data="download")
    )
    kb.row(
        InlineKeyboardButton(text="🤝 Рефералы", callback_data="referrals"),
        InlineKeyboardButton(text="💳 Выбор тарифа", callback_data="buy")
    )
    return kb.as_markup()

def buy_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="👨‍💻 Написать админу", url=ADMIN_USERNAME))
    kb.row(back_button)
    return kb.as_markup()

def extend_sub_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="💎 Продлить подписку", url=ADMIN_USERNAME))
    return kb.as_markup()

def to_main_kb():
    kb = InlineKeyboardBuilder()
    kb.row(back_button)
    return kb.as_markup()