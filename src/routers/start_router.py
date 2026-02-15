from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

start_router = Router(name="start_router")

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🚀 ПОДКЛЮЧИТЬ ОБХОД", callback_data="get_link"))
    kb.row(
        types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        types.InlineKeyboardButton(text="📥 Софт", callback_data="download")
    )
    kb.row(types.InlineKeyboardButton(text="💳 Продлить доступ", callback_data="buy"))
    return kb.as_markup()

# --- Роут /start ---

@start_router.message(Command("start"))
async def start(message: types.Message):
    # Заглушка времени (типа на 24 часа от текущего момента)
    trial_end = (datetime.now() + timedelta(hours=24)).strftime("%H:%M %d.%m.%Y")
    
    text = (
        f"🎁 **ТРИАЛ АКТИВИРОВАН!**\n\n"
        f"Тебе выдано **24 часа** бесплатного доступа.\n"
        f"Трафик: **Безлимит** ♾\n"
        f"Истекает: `{trial_end}`\n\n"
        "Жми на кнопку ниже, забирай ссылку и вставляй в приложение."
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu())

# --- Обработка кнопок ---

@start_router.callback_query(F.data == "get_link")
async def send_link(call: types.CallbackQuery):
    # Чисто заглушечная VLESS ссылка
    fake_vless = "vless://fake-uuid-12345@server.host:443?security=reality&sni=google.com&pbk=key&fp=chrome&type=grpc#Access_Granted"
    
    text = (
        "🔗 **Твоя ссылка для приложения:**\n\n"
        f"`{fake_vless}`\n\n"
        "👆 **Нажми, чтобы скопировать.**\n"
        "Вставь её в софт и нажми **«Включить»**."
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=main_menu())

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
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

@start_router.callback_query(F.data == "buy")
async def buy(call: types.CallbackQuery):
    text = (
        "💳 **ОПЛАТА (ЗАГЛУШКА)**\n\n"
        "• 1 месяц — 199₽\n"
        "• 3 месяца — 499₽\n\n"
        "⚠️ Сейчас оплата только через админа."
    )
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="👨‍💻 Написать админу", url="https://t.me"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main"))
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

@start_router.callback_query(F.data == "to_main")
async def to_main(call: types.CallbackQuery):
    await start(call.message)
    await call.answer()