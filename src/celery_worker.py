from celery import Celery
from config import REDIS_URL, API_TOKEN
from redis.asyncio import from_url
from aiogram import Bot
import time
import asyncio
from parser import GooFishParser

worker = Celery(__name__)
worker.conf.broker_url = REDIS_URL
worker.conf.result_backend = REDIS_URL

def stop_tasks_by_arg(target_arg1):
    inspector = worker.control.inspect()
    
    task_sources = [inspector.active(), inspector.scheduled(), inspector.reserved()]
    
    for source in task_sources:
        if not source: continue
        
        for _, tasks in source.items():
            for task in tasks:
                if task['args'] and str(task['args'][0]) == str(target_arg1):
                    print(f"Revoking task {task['id']} for arg {target_arg1}")
                    worker.control.revoke(task['id'], terminate=True, signal='SIGTERM')

async def parse_async(telegram_id: int, query: str):
    try:
        parser = GooFishParser()
        redis_client = from_url(REDIS_URL)
        bot = Bot(API_TOKEN)
        print("OKI")
        count = 0

        async for card in parser.run(query):
            try:
                caption = (
                    f"📝 <b>Описание:</b>\n<i>{card.description[:150]}...</i>\n\n"
                    f"💰 <b>Цена:</b> <code>{card.cny_price}</code>\n"
                    f"📏 <b>Размер:</b> <code>{card.size or 'Не указан'}</code>\n"
                    f"📍 <b>Локация:</b> {card.location}\n\n"
                    f"🔗 <a href='{card.link}'>Открыть товар</a>"
                )
                await bot.send_photo(
                    chat_id=telegram_id,
                    photo=card.image_uri,
                    caption=caption,
                    parse_mode="HTML"
                )
                count += 1
            except Exception:
                await bot.send_message(
                    chat_id=telegram_id,
                    text=f"🖼 <i>(Фото недоступно)</i>\n\n{caption}",
                    parse_mode="HTML",
                    disable_web_page_preview=False
                )
                count += 1

        summary_text = (
            "<b>✅ Парсинг завершен!</b>\n\n"
            f"🔍 <b>Запрос:</b> <code>{query}</code>\n"
            f"📦 <b>Найдено товаров:</b> <code>{count}</code>\n\n"
            "<i>Все актуальные предложения отправлены выше. Выберите следующее действие в меню:</i>"
        )

        await bot.send_message(
            chat_id=telegram_id,
            text=summary_text,
            parse_mode="HTML"
        )
        await redis_client.delete(f"parse_{telegram_id}")
        await redis_client.aclose()
    finally:
        if bot.session:
            await bot.session.close()

@worker.task(name='parse_goofish')
def parse_goofish(telegram_id: int, query: str):
    asyncio.run(parse_async(telegram_id, query))