from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from utils import bytes_to_gb, ms_to_datetime
from db import get_user_by_tg_id, update_user_uuid
from create_bot import three_xui_clients

ADMINS = [1715446082]

admin_router = Router(name="admin_router")

class AdminStates(StatesGroup):
    wait_user_id = State()
    server = State()
    sub_info = State()
    client_uuid = State()

@admin_router.message(Command("admin"), F.from_user.id.in_(ADMINS))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🛠 <b>Админ-панель 3x-ui</b>\n\n"
        "Отправьте <b>Telegram ID</b> пользователя для управления подпиской:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.wait_user_id)

@admin_router.message(AdminStates.wait_user_id, F.from_user.id.in_(ADMINS))
async def user_manage_menu(message: Message, session: AsyncSession, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❌ Ошибка: ID должен быть числом.")
    
    target_id = int(message.text)
    user = await get_user_by_tg_id(session, target_id)
    if not user:
        await state.clear()
        return await message.answer("❌ Пользователь не найден")
    
    server = three_xui_clients.get(user.server_id)
    if not server:
        await state.clear()
        return await message.answer("❌ Ошибка: клиент не привязан к серверу")

    sub_info = await server.get_client_stats(user.uuid)

    await state.update_data(
        target_id=target_id,
        client_uuid=user.uuid,
        server=server,
        sub_info=sub_info
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Продлить (1 мес)", callback_data="adm_extend_1")],
        [InlineKeyboardButton(text="➕ Продлить (3 мес)", callback_data="adm_extend_3")],
        [InlineKeyboardButton(text="➕ Продлить (6 мес)", callback_data="adm_extend_6")],
        [InlineKeyboardButton(text="❄️ Заморозить / Разморозить", callback_data="adm_freeze")],
        [InlineKeyboardButton(text="🗑 Удалить подписку", callback_data="adm_delete")],
        [InlineKeyboardButton(text="⬅️ Назад к поиску", callback_data="adm_back")]
    ])

    sub_text = "Нет активной подписки"
    if sub_info:
        sub_text = (
            f"📈 Трафик: {bytes_to_gb(sub_info.total)} ГБ\n"
            f"🆔 UUID: {user.uuid}\n"
            f"🖥 Сервер: {server.data.get('host')}\n"
            f"⏳ Срок: до {ms_to_datetime(sub_info.expiryTime)}\n"
            f"✅ Статус: {"Активна" if sub_info.active else "Неактивна"}\n"
        )

    await message.answer(
        f"👤 <b>Управление пользователем:</b> <code>{target_id}</code>\n"
        f"----------------------------------\n"
        f"{sub_text}"
        f"----------------------------------",
        reply_markup=kb,
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data.startswith("adm_"), F.from_user.id.in_(ADMINS))
async def process_admin_action(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")
    
    if not target_id:
        return await call.answer("Ошибка: сессия истекла", show_alert=True)

    action = call.data.replace("adm_", "")
    server = data.get("server")
    client_uuid = data.get('client_uuid')
    sub_info = data.get('sub_info')

    if action == "extend_1":
        success = await server.extend_client_subscription(
            client_uuid,
            sub_info,
            30
        )
        if success:
            await call.answer(f"✅ Пользователю добавлено 1 месяц подписки", show_alert=True)
        else:
            await call.answer("❌ Произошла ошибка", show_alert=True)

    elif action == "extend_3":
        success = await server.extend_client_subscription(
            client_uuid,
            sub_info,
            90
        )
        if success:
            await call.answer(f"✅ Пользователю добавлено 3 месяца подписки", show_alert=True)
        else:
            await call.answer("❌ Произошла ошибка", show_alert=True)

    elif action == "extend_6":
        success = await server.extend_client_subscription(
            client_uuid,
            sub_info,
            180
        )
        if success:
            await call.answer(f"✅ Пользователю добавлено полгода подписки", show_alert=True)
        else:
            await call.answer("❌ Произошла ошибка", show_alert=True)

    elif action == "freeze":
        state = not sub_info.enabled
        success = await server.toggle_client_status(client_uuid, sub_info, state)
        if not success:
            await call.answer("❌ Произошла ошибка", show_alert=True)
            
        if not state:
            await call.answer("❄️ Подписка заморожена", show_alert=True)
        else:
            await call.answer("❄️ Подписка разморожена", show_alert=True)

    elif action == "delete":
        success = await server.delete_client(client_uuid)
        if not success:
            await call.answer("❌ Произошла ошибка", show_alert=True)

        await update_user_uuid(session, target_id, None)
        await call.answer("🗑 Подписка полностью удалена", show_alert=True)
        await call.message.edit_text("❌ Подписка удалена")
        return

    elif action == "back":
        await state.clear()
        await call.message.edit_text("Введите Telegram ID пользователя:")
        await state.set_state(AdminStates.wait_user_id)
        await call.answer()
        return

    await call.answer()
