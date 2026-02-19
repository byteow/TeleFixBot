import asyncio
from create_bot import dp, bot, set_servers, three_xui_clients
from routers import user_router, admin_router
from middlewares import DatabaseSessionMiddleware, RegistrationMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils import get_now_ms
from keyboards import extend_sub_kb

async def check_subscriptions():
    now_ms = get_now_ms()
    one_day_ms = 24 * 60 * 60 * 1000
    three_days_ms = 3 * one_day_ms
    
    kb = extend_sub_kb()

    for server in three_xui_clients.values():
        clients = await server.get_all_clients_expiry()
        if not clients:
            continue
            
        for client in clients:
            expiry_time = client.get('expiryTime', 0)
            tg_id = client.get('tgId')
            if expiry_time <= 0 or not tg_id:
                continue

            if now_ms >= expiry_time:
                text = (
                    f"<b>❌ Доступ приостановлен</b>\n\n"
                    f"Ваша подписка закончилась\n"
                    f"Подключение отключено. Чтобы продолжить пользоваться сервисом, продлите подписку."
                )
                try:
                    await bot.send_message(tg_id, text, parse_mode='HTML', reply_markup=kb)
                except Exception:
                    pass

            elif 0 < (expiry_time - now_ms) <= one_day_ms:
                text = (
                    f"<b>⚠️ Подписка почти истекла!</b>\n\n"
                    f"Уведомляем вас, что через 24 часа срок действия вашей подписки истечет.\n"
                    f"Рекомендуем продлить доступ сейчас, чтобы избежать прерывания соединения."
                )
                try:
                    await bot.send_message(tg_id, text, parse_mode='HTML', reply_markup=kb)
                except Exception:
                    pass

            elif one_day_ms * 2 < (expiry_time - now_ms) <= three_days_ms:
                text = (
                    f"<b>⏳ Скоро окончание подписки</b>\n\n"
                    f"Уведомляем вас, что через 3 дня срок действия вашей подписки истечет.\n"
                    f"Заранее пополните баланс, если планируете продолжать использование."
                )
                try:
                    await bot.send_message(tg_id, text, parse_mode='HTML')
                except Exception:
                    pass

async def main():
    await set_servers()

    dp.update.outer_middleware(DatabaseSessionMiddleware())
    dp.update.outer_middleware(RegistrationMiddleware())
    dp.include_router(user_router)
    dp.include_router(admin_router)

    scheduler = AsyncIOScheduler()

    scheduler.add_job(check_subscriptions, 'cron', hour=12, args=[])
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())