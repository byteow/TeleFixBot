import asyncio
from create_bot import dp, bot, set_servers
from routers import user_router, admin_router
from middlewares import DatabaseSessionMiddleware, RegistrationMiddleware

async def main():
    await set_servers()

    dp.update.outer_middleware(DatabaseSessionMiddleware())
    dp.update.outer_middleware(RegistrationMiddleware())
    dp.include_router(user_router)
    dp.include_router(admin_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())