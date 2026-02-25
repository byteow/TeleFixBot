from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from utils import bytes_to_gb, ms_to_datetime
from services import get_server_by_id
from db import get_user_by_tg_id, update_user_uuid, get_users_telegram_ids
from create_bot import bot
from config import ADMINS
from middlewares import stats_cache

async def notify_renewed(chat_id: int, add_days: int):
    text = (
        "<b>✅ Подписка продлена администратором</b>\n\n"
        f"Оплата прошла успешно. Вам добавлено {add_days} дней подписки\n"
        "Спасибо, что остаетесь с нами!"
    )
    await bot.send_message(chat_id, text, parse_mode="HTML")

async def notify_frozen(chat_id: int):
    text = (
        "<b>❄️ Подписка заморожена администратором</b>\n\n"
        "Доступ к платным функциям временно приостановлен. "
    )
    await bot.send_message(chat_id, text, parse_mode="HTML")

async def notify_unfrozen(chat_id: int):
    text = (
        "<b>🔥 Подписка разморожена администратором</b>\n\n"
        "С возвращением! Платный доступ снова активен, и вы можете продолжать работу в обычном режиме."
    )
    await bot.send_message(chat_id, text, parse_mode="HTML")

async def notify_deleted(chat_id: int):
    text = (
        "<b>❌ Подписка аннулирована администратором</b>\n\n"
        "Срок действия вашей подписки истек или она была отменена. "
    )
    await bot.send_message(chat_id, text, parse_mode="HTML")

admin_router = Router(name="admin_router")

class AdminStates(StatesGroup):
    wait_user_id = State()
    server = State()
    sub_info = State()
    client_uuid = State()

class BroadcastState(StatesGroup):
    msg = State()

@admin_router.message(Command("admin"), F.from_user.id.in_(ADMINS))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🛠 <b>Админ-панель</b>\n\n"
        "Отправьте <b>Telegram ID</b> пользователя для управления подпиской:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.wait_user_id)

@admin_router.message(Command("broadcast"), F.from_user.id.in_(ADMINS))
async def broadcast_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🛠 <b>Рассылка сообщений</b>\n\n"
        "Напишите сообщение, которое надо отправить:",
        parse_mode="HTML"
    )
    await state.set_state(BroadcastState.msg)

@admin_router.message(BroadcastState.msg, F.from_user.id.in_(ADMINS))
async def broadcast(message: Message, session: AsyncSession, state: FSMContext):
    ids = await get_users_telegram_ids(session)
    await message.answer(text="ℹ️ Начинаем пересылать")
    for _id in ids:
        try:
            if _id == message.from_user.id:
                continue
            await message.copy_to(chat_id=_id)
        except Exception:
            ...

    await state.clear()
    await message.answer(text="✅ Пересылка закончена")

@admin_router.message(AdminStates.wait_user_id, F.from_user.id.in_(ADMINS))
async def user_manage_menu(message: Message, session: AsyncSession, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❌ Ошибка: ID должен быть числом.")
    
    target_id = int(message.text)
    user = await get_user_by_tg_id(session, target_id)
    if not user:
        await state.clear()
        return await message.answer("❌ Пользователь не найден")
    
    server = get_server_by_id(user.server_id)
    if not server:
        await state.clear()
        return await message.answer("❌ Ошибка: клиент не привязан к серверу")

    sub_info = await server.get_client_stats(user.telegram_id)

    await state.update_data(
        target_id=target_id,
        client_uuid=user.uuid,
        server=server,
        sub_info=sub_info
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Продлить (24 часа)", callback_data="adm_extend_1")],
        [InlineKeyboardButton(text="➕ Продлить (1 мес)", callback_data="adm_extend_30")],
        [InlineKeyboardButton(text="➕ Продлить (3 мес)", callback_data="adm_extend_90")],
        [InlineKeyboardButton(text="➕ Продлить (6 мес)", callback_data="adm_extend_180")],
        [InlineKeyboardButton(text="❄️ Заморозить / Разморозить", callback_data="adm_freeze")],
        [InlineKeyboardButton(text="🗑 Удалить подписку", callback_data="adm_delete")],
        [InlineKeyboardButton(text="⬅️ Назад к поиску", callback_data="adm_back")]
    ])

    sub_text = "Нет активной подписки"
    if sub_info:
        sub_text = (
            f"📈 Трафик: {bytes_to_gb(sub_info.total)} ГБ\n"
            f"🆔 UUID: {user.uuid}\n"
            f"🖥 Сервер: {server.model.host}\n"
            f"⏳ Срок: до {ms_to_datetime(sub_info.expiryTime)}\n"
            f"✅ Статус: {"Активна" if sub_info.active else "Неактивна"}"
        )

    await message.answer(
        f"👤 <b>Управление пользователем:</b> <code>{target_id}</code>\n"
        f"----------------------------------\n"
        f"{sub_text}\n"
        f"----------------------------------",
        reply_markup=kb,
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data.startswith("adm_"), F.from_user.id.in_(ADMINS))
async def process_admin_action(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")
    
    if not target_id:
        return await call.answer("❌ Ошибка: сессия истекла", show_alert=True)

    action = call.data.replace("adm_", "")
    server = data.get("server")
    client_uuid = data.get('client_uuid')
    sub_info = data.get('sub_info')

    if "extend" in action and len(action.split("_")) > 1:
        add_days = action.split("_")[-1]
        if add_days.isdigit():
            add_days = int(add_days)
            if add_days <= 0 or add_days > 180:
                return
        else:
            return
        result = await server.extend_client_subscription(
            client_uuid,
            target_id,
            sub_info,
            add_days
        )
        if type(result) == str:
            await update_user_uuid(session, target_id, result)
        if result:
            await call.answer(f"✅ Пользователю добавлено {add_days} дней подписки", show_alert=True)
            await notify_renewed(target_id, add_days)
            stats_cache.pop(target_id)
        else:
            await call.answer("❌ Произошла ошибка", show_alert=True)

    elif action == "freeze":
        state = not sub_info.enable
        success = await server.toggle_client_status(client_uuid, target_id, sub_info, state)
        if not success:
            await call.answer("❌ Произошла ошибка", show_alert=True)
            
        if not state:
            await call.answer("❄️ Подписка заморожена", show_alert=True)
            await notify_frozen(target_id)
        else:
            await call.answer("❄️ Подписка разморожена", show_alert=True)
            await notify_unfrozen(target_id)
        stats_cache.pop(target_id)

    elif action == "delete":
        success = await server.delete_client(client_uuid)
        if not success:
            await call.answer("❌ Произошла ошибка", show_alert=True)

        await update_user_uuid(session, target_id, None)
        await call.answer("🗑 Подписка полностью удалена", show_alert=True)
        await call.message.edit_text("❌ Подписка удалена")
        await notify_deleted(target_id)
        stats_cache.pop(target_id)
        return

    elif action == "back":
        await state.clear()
        await call.message.edit_text("Введите Telegram ID пользователя:")
        await state.set_state(AdminStates.wait_user_id)
        await call.answer()
        return

    await call.answer()
