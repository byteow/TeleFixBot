from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
from services import SubscribeInfo
from db import User
from utils import ms_to_datetime, generate_vless_link
from create_bot import bot
from config import ADMIN_USERNAME

start_router = Router(name="start_router")

photo_path = os.path.join("src", "photos", "logo.png")
photo = FSInputFile(photo_path)

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🚀 ПОДКЛЮЧИТЬ ОБХОД", callback_data="get_link"))
    kb.row(
        types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        types.InlineKeyboardButton(text="📥 Софт", callback_data="download")
    )
    kb.row(types.InlineKeyboardButton(text="💳 Продлить доступ", callback_data="buy"))
    return kb.as_markup()

def buy_kb():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="👨‍💻 Написать админу", url=ADMIN_USERNAME))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main"))
    return kb.as_markup()

def get_main_text(message: Message, is_reg: bool, sub_info: SubscribeInfo | None):
    text = (
        "🔴 **ДОСТУП ОГРАНИЧЕН**\n\n"
        "Твоя подписка истекла или еще не была активирована. 🛑\n"
        "Трафик: **0 MB** ❌\n"
        "Статус: `Отключено` 🔌\n\n"
        "Чтобы продолжить пользоваться быстрым интернетом без границ, "
        "продли доступ в разделе **«Купить подписку»**."
    )
    if sub_info and sub_info.enable:
        end_date = ms_to_datetime(sub_info.expiryTime)
        if is_reg:
            text = (
                f"🎁 **ТРИАЛ АКТИВИРОВАН!**\n\n"
                f"Тебе выдано **24 часа** бесплатного доступа.\n"
                f"Трафик: **Безлимит** ♾\n"
                f"Истекает: `{end_date}`\n\n"
                "Жми на кнопку ниже, забирай ссылку и вставляй в приложение."
            )
        else:
            text = (
                f"👋 **С возвращением, {message.from_user.first_name}!**\n\n"
                f"🔒 **Твой доступ:** `Активен` ✅\n"
                f"📅 **Истекает:** `{end_date}`\n\n"
                "Обход работает в штатном режиме. "
                "Если нужно обновить настройки или скачать софт — воспользуйся кнопками ниже. 👇"
            )
    return text

def get_payment_text(no_sub: bool):
    title = "Чтобы подключить обход нужнно оформить подписку" if no_sub else "ОПЛАТА"
    text = (
        f"💳 **{title}**\n\n"
        "**• 1 месяц — 100₽**\n"
        "**• 3 месяца — 250₽**\n"
        "**• 3 месяца — 450₽**\n\n"
        "⚠️ Сейчас оплата только через админа."
    )
    return text

@start_router.message(Command("start"))
async def start(message: types.Message, user: User, is_reg: bool, sub_info: SubscribeInfo | None):
    await bot.send_photo(
        chat_id=message.from_user.id,
        caption=get_main_text(message, is_reg, sub_info), 
        photo=photo,
        parse_mode="Markdown", 
        reply_markup=main_menu()
    )

@start_router.callback_query(F.data == "get_link")
async def send_link(call: types.CallbackQuery, server_data: dict, user: User, sub_info: SubscribeInfo | None):
    text=get_payment_text(True)
    kb = buy_kb()
    if sub_info and sub_info.enable:
        link = generate_vless_link(server_data, user.uuid)
        text = (
            "🔗 **Твоя ссылка для приложения:**\n\n"
            f"`{link}`\n\n"
            "👆 **Нажми, чтобы скопировать.**\n"
            "Вставь её в софт и нажми **«Включить»**."
        )
        kb = main_menu()
    await call.message.edit_caption(caption=text, parse_mode="Markdown", reply_markup=kb)

@start_router.callback_query(F.data == "profile")
async def profile(call: types.CallbackQuery):
    text = (
        "👤 **АККАУНТ: ТЕСТОВЫЙ**\n\n"
        "📊 Трафик: `Unlimited` ♾\n"
        "📅 Доступ до: `Завтра (24ч)`\n"
        "🌐 Статус: `Подключено` ✅"
    )
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="💳 Купить подписку", callback_data="buy"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main"))
    await call.message.edit_caption(caption=text, parse_mode="Markdown", reply_markup=kb.as_markup())

@start_router.callback_query(F.data == "buy")
async def buy(call: types.CallbackQuery):
    await call.message.edit_caption(caption=get_payment_text(False), parse_mode="Markdown", reply_markup=buy_kb())

@start_router.callback_query(F.data == "to_main")
async def to_main(call: types.CallbackQuery, is_reg: bool, sub_info: SubscribeInfo | None):
    await call.message.edit_caption(
        caption=get_main_text(call.message, is_reg, sub_info),
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
    await call.answer()