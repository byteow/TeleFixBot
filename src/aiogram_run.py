import asyncio
from create_bot import dp, bot
from routers import start_router
from middlewares import DatabaseSessionMiddleware

async def main():
    dp.update.outer_middleware(DatabaseSessionMiddleware())
    dp.include_router(start_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())