from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.types import Message, InputMediaPhoto
from services import SubscribeInfo
from db import User
from utils import ms_to_datetime, generate_vless_link
from create_bot import bot
from constants import (
    logo_photo, 
    virus_total_photo, 
    win_link, 
    linux_link, 
    mac_link, 
    vt_report
)
from keyboards import main_menu, to_main_kb, buy_kb

user_router = Router(name="user_router")

def get_main_text(message: Message, is_reg: bool, sub_info: SubscribeInfo | None):
    text = (
        "🔴 **ДОСТУП ОГРАНИЧЕН**\n\n"
        "Твоя подписка истекла или еще не была активирована. 🛑\n"
        "Трафик: **0 MB** ❌\n"
        "Статус: `Отключено` 🔌\n\n"
        "Чтобы продолжить пользоваться быстрым интернетом без границ, "
        "продли доступ в разделе **«Купить подписку»**."
    )

    if sub_info and sub_info.active:
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
    title = "На данный момент на вашем аккаунте нет активной подписки" if no_sub else "ОПЛАТА"
    text = (
        f"💳 **{title}**\n\n"
        "**• 1 месяц — 100₽**\n"
        "**• 3 месяца — 250₽**\n"
        "**• 3 месяца — 450₽**\n\n"
        "⚠️ Сейчас оплата только через админа."
    )
    return text

@user_router.message(Command("start"))
async def start(message: types.Message, is_reg: bool, sub_info: SubscribeInfo | None):
    await bot.send_photo(
        chat_id=message.from_user.id,
        caption=get_main_text(message, is_reg, sub_info), 
        photo=logo_photo,
        parse_mode="Markdown", 
        reply_markup=main_menu()
    )

@user_router.callback_query(F.data == "download")
async def download(call: types.CallbackQuery):
    text = (
        "<b>🚀 Наше фирменное приложение</b>\n\n"
        "Пользуйтесь интернетом без границ с помощью нашего клиента. "
        "Мы сделали его максимально легким и быстрым.\n\n"
        "<b>📥 Скачать для своей ОС:</b>\n"
        f"└ <a href='{win_link}'>Windows</a> | "
        f" <a href='{mac_link}'>macOS</a> | "
        f" <a href='{linux_link}'>Linux</a>\n\n"
        "<b>🛡 Безопасность превыше всего:</b>\n"
        "Приложение полностью чистое. Мы дорожим своей репутацией, поэтому "
        "каждая сборка проходит автоматическую проверку.\n"
        f"✅ <b><a href='{vt_report}'>Посмотреть отчет VirusTotal</a></b>\n\n"
        "<i>🦾 Никаких скрытых майнеров или вирусов — только чистый код для вашего обхода.</i>"
    )

    new_media = InputMediaPhoto(
        media=virus_total_photo, 
        caption=text,
        parse_mode="HTML"   
    )

    await call.message.edit_media(
        media=new_media,
        reply_markup=to_main_kb()
    )
    await call.answer()

@user_router.callback_query(F.data == "get_link")
async def send_link(call: types.CallbackQuery, server_data: dict, user: User, sub_info: SubscribeInfo | None):
    text = get_payment_text(True)
    kb = buy_kb()
    if sub_info and sub_info.active:
        link = generate_vless_link(server_data, user.uuid)
        text = (
            "🔗 **Твоя ссылка для приложения:**\n\n"
            f"`{link}`\n\n"
            "👆 **Нажми, чтобы скопировать.**\n"
            "Вставь её в софт и нажми **«Включить»**."
        )
        kb = to_main_kb()
    await call.message.edit_caption(caption=text, parse_mode="Markdown", reply_markup=kb)

@user_router.callback_query(F.data == "about_subscribe")
async def about_subscribe(call: types.CallbackQuery, user: User, server_data: dict, sub_info: SubscribeInfo | None):
    text = get_payment_text(True)
    kb = to_main_kb()

    if sub_info and sub_info.active:
        text = (
            "**ℹ️ О подписке**\n\n"
            f"🆔 UUID: `{user.uuid}`\n"
            f"🖥 Сервер: {server_data.get("host")}\n"
            f"📅 Активна до: {ms_to_datetime(sub_info.expiryTime)}\n"
            f"✅ Статус: Активна\n\n"
        )

    await call.message.edit_caption(caption=text, parse_mode="Markdown", reply_markup=kb)

@user_router.callback_query(F.data == "buy")
async def buy(call: types.CallbackQuery):
    await call.message.edit_caption(caption=get_payment_text(False), parse_mode="Markdown", reply_markup=buy_kb())

@user_router.callback_query(F.data == "to_main")
async def to_main(call: types.CallbackQuery, is_reg: bool, sub_info: SubscribeInfo | None):
    new_media = InputMediaPhoto(
        media=logo_photo, 
        caption=get_main_text(call.message, is_reg, sub_info),
        parse_mode="Markdown",
    )
    await call.message.edit_media(
        media=new_media,
        reply_markup=main_menu()
    )
    await call.answer()