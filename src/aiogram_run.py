import asyncio
from create_bot import dp, bot, set_servers
from routers import start_router
from middlewares import DatabaseSessionMiddleware, RegistrationMiddleware

async def main():
    await set_servers()

    dp.update.outer_middleware(DatabaseSessionMiddleware())
    dp.update.outer_middleware(RegistrationMiddleware())
    dp.include_router(start_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())