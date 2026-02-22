from aiogram import types, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import InputMediaPhoto
from services import SubscribeInfo, get_server_by_id
from db import (
    User, 
    get_referrals_count, 
    get_referral, 
    create_referral,
    get_user_by_tg_id
)
from sqlalchemy.ext.asyncio import AsyncSession
from utils import (
    ms_to_datetime, 
    generate_vless_link, 
    generate_referral_link
)
from create_bot import bot
from constants import (
    logo_photo, 
    virus_total_photo
)
from config import (
    SOFT_LINUX_LINK,
    SOFT_MAC_LINK,
    SOFT_WIN_LINK,
    VIRUS_TOTAL_LINK
)
from keyboards import main_menu, to_main_kb, buy_kb

user_router = Router(name="user_router")

def get_main_text(is_reg: bool, sub_info: SubscribeInfo | None):
    text = (
        "🔴 <b>ДОСТУП ОГРАНИЧЕН</b>\n\n"
        "Твоя подписка истекла или еще не была активирована. 🛑\n"
        "Трафик: <b>0 MB</b> ❌\n"
        "Статус: <code>Отключено</code> 🔌\n\n"
        "Чтобы продолжить пользоваться быстрым интернетом без границ, "
        "продли доступ в разделе <b>«Купить подписку»</b>."
    )

    if sub_info and sub_info.active:
        end_date = ms_to_datetime(sub_info.expiryTime)
        if is_reg:
            text = (
                f"🎁 <b>ТРИАЛ АКТИВИРОВАН!</b>\n\n"
                f"Тебе выдано <b>24 часа</b> бесплатного доступа.\n"
                f"Трафик: <b>Безлимит</b> ♾\n"
                f"Истекает: <code>Завтра</code>\n\n"
                "Жми на кнопку ниже, забирай ссылку и вставляй в приложение."
            )
        else:
            text = (
                f"👋 <b>С возвращением!</b>\n\n"
                f"🔒 <b>Твой доступ:</b> <code>Активен</code> ✅\n"
                f"📅 <b>Истекает:</b> <code>{end_date}</code>\n\n"
                "Обход работает в штатном режиме. "
                "Если нужно обновить настройки или скачать софт — воспользуйся кнопками ниже. 👇"
            )
    return text

def get_payment_text(no_sub: bool):
    title = "На данный момент на вашем аккаунте нет активной подписки" if no_sub else "ОПЛАТА"
    text = (
        f"💳 <b>{title}</b>\n\n"
        "<b>• 1 месяц   — 100₽</b>\n"
        "<b>• 3 месяца  — 250₽</b>\n"
        "<b>• 6 месяцев — 450₽</b>\n\n"
        "⚠️ Сейчас оплата только через админа."
    )
    return text

@user_router.message(Command("start"))
async def start(message: types.Message, session: AsyncSession, command: CommandObject, is_reg: bool, sub_info: SubscribeInfo | None):
    try:
        args = command.args
        if args and args.startswith("referral_") and is_reg:
            referrer_id = int(args.split("_")[-1])
            if referrer_id != message.from_user.id:
                ref = await get_referral(session, referrer_id, message.from_user.id)
                if not ref:
                    referrer = await get_user_by_tg_id(session, referrer_id)
                    if referrer:
                        await create_referral(
                            session,
                            referrer_id,
                            message.from_user.id
                        )
                        server = get_server_by_id(referrer.server_id)
                        if server:
                            sub_info = await server.get_client_stats(referrer.telegram_id)
                            success = await server.extend_client_subscription(
                                referrer.uuid,
                                referrer.telegram_id,
                                sub_info,
                                1
                            )
                            if success:
                                await bot.send_message(
                                    referrer.telegram_id, 
                                    text=(
                                        f"🔔 <b>Новый реферал!</b>\n\n"
                                        f"По вашей ссылке перешел: {message.from_user.full_name}\n"
                                        "🎁 Вам было добавлено <b>+24 часа</b> подписки!"
                                    ),
                                    parse_mode="HTML"
                                )
    except Exception as e:
        print("Referral exception:", e)
    
    await bot.send_photo(
        chat_id=message.from_user.id,
        caption=get_main_text(is_reg, sub_info), 
        photo=logo_photo,
        parse_mode="HTML", 
        reply_markup=main_menu()
    )

@user_router.callback_query(F.data == "download")
async def download(call: types.CallbackQuery):
    text = (
        "<b>🚀 Наше фирменное приложение</b>\n\n"
        "Пользуйтесь Telegram без границ с помощью нашего клиента. "
        "Мы сделали его максимально легким и быстрым.\n\n"
        "<b>📥 Скачать для своей ОС:</b>\n"
        f"└ <a href='{SOFT_WIN_LINK}'>Windows</a> | "
        f" <a href='{SOFT_MAC_LINK}'>macOS</a> | "
        f" <a href='{SOFT_LINUX_LINK}'>Linux</a>\n\n"
        "<b>🛡 Безопасность превыше всего:</b>\n"
        "Приложение полностью чистое. Мы дорожим своей репутацией, поэтому "
        "каждая сборка проходит автоматическую проверку.\n"
        f"✅ <b><a href='{VIRUS_TOTAL_LINK}'>Посмотреть отчет VirusTotal</a></b>\n\n"
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
            "🔗 <b>Твоя ссылка для приложения:</b>\n\n"
            f"<code>{link}</code>\n\n"
            "👆 <b>Нажми, чтобы скопировать.</b>\n"
            "Вставь её в софт и нажми <b>«Включить»</b>."
        )
        kb = to_main_kb()
    await call.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)

@user_router.callback_query(F.data == "referrals")
async def referrals(call: types.CallbackQuery, user: User, session: AsyncSession):
    count = await get_referrals_count(session, user.telegram_id) 
    
    text = (
        "<b>👥 Реферальная программа</b>\n\n"
        "Ваша реферальная ссылка:\n"
        f"<code>{generate_referral_link(user.telegram_id)}</code>\n\n"
        f"• Количество ваших рефералов: <b>{count}</b>\n\n"
        "<i>ℹ️ За каждого приведённого пользователя вам будет начислено + 24 часа подписки</i>"
    )
    
    kb = to_main_kb()
    await call.message.edit_caption(
        caption=text, 
        parse_mode="HTML",
        reply_markup=kb
    )

@user_router.callback_query(F.data == "about_subscribe")
async def about_subscribe(call: types.CallbackQuery, user: User, server_data: dict, sub_info: SubscribeInfo | None):
    text = get_payment_text(True)
    kb = to_main_kb()

    if sub_info and sub_info.active:
        text = (
            "<b>ℹ️ О подписке</b>\n\n"
            f"🆔 UUID: <code>{user.uuid}</code>\n"
            f"🖥 Сервер: {server_data.get("host")}\n"
            f"📅 Активна до: <code>{ms_to_datetime(sub_info.expiryTime)}</code>\n"
            f"✅ Статус: <code>Активна</code>\n\n"
        )

    await call.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)

@user_router.callback_query(F.data == "buy")
async def buy(call: types.CallbackQuery):
    await call.message.edit_caption(caption=get_payment_text(False), parse_mode="HTML", reply_markup=buy_kb())

@user_router.callback_query(F.data == "to_main")
async def to_main(call: types.CallbackQuery, is_reg: bool, sub_info: SubscribeInfo | None):
    new_media = InputMediaPhoto(
        media=logo_photo, 
        caption=get_main_text(is_reg, sub_info),
        parse_mode="HTML",
    )
    await call.message.edit_media(
        media=new_media,
        reply_markup=main_menu()
    )
    await call.answer()