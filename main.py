import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from config import BOT_TOKEN, CHECK_INTERVAL
from keyboard.inline import get_main_reply_keyboard
from services.logger import setup_logging
from services.notifier import notify_new_accounts

setup_logging()
logger = logging.getLogger(__name__)

dp = Dispatcher()
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message(F.text == "/start")
async def start(message: Message):
    logger.info("Получена команда /start от chat_id=%s", message.chat.id)
    await message.answer(
        "👋 Привет! Выберите действие:", reply_markup=get_main_reply_keyboard()
    )
    # asyncio.create_task(notify_new_accounts(bot, message.chat.id, CHECK_INTERVAL))


@dp.message(F.text == "🚀 Начать отслеживание")
async def start_tracking(message: Message, bot: Bot):
    logger.info("Запуск отслеживания для chat_id=%s", message.chat.id)
    await message.answer("🔍 Начинаю отслеживать аккаунты...")
    asyncio.create_task(notify_new_accounts(bot, message.chat.id, CHECK_INTERVAL))


@dp.message(F.text == "⚙️ Фильтры")
async def handle_filters(message: Message):
    await message.answer("⚙️ Настройка фильтров пока в разработке.")


async def main():
    logger.info("Старт поллинга бота")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
