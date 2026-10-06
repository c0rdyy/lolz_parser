from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
import asyncio
import logging

from services.logger import setup_logging
from services.notifier import notify_new_accounts
from keyboard.inline import get_main_reply_keyboard
from config import BOT_TOKEN, CHECK_INTERVAL
from services.market_client import buy_item, get_fortnite_accounts, save_to_json_default

setup_logging()
logger = logging.getLogger(__name__)

dp = Dispatcher()
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))



@dp.message(F.text == "/start")
async def start(message: Message):
    logger.info("Получена команда /start от chat_id=%s", message.chat.id)
    await message.answer("👋 Привет! Выберите действие:",
        reply_markup=get_main_reply_keyboard())
    # asyncio.create_task(notify_new_accounts(bot, message.chat.id, CHECK_INTERVAL))

@dp.message(F.text == "🚀 Начать отслеживание")
async def start_tracking(message: Message, bot: Bot):
    logger.info("Запуск отслеживания для chat_id=%s", message.chat.id)
    await message.answer("🔍 Начинаю отслеживать аккаунты...")
    asyncio.create_task(notify_new_accounts(bot, message.chat.id, CHECK_INTERVAL))

@dp.message(F.text == "⚙️ Фильтры")
async def handle_filters(message: Message):
    await message.answer("⚙️ Настройка фильтров пока в разработке.")

@dp.message(F.text == "buy")
async def test(message: Message):
    # await test_resell_one_account()
    success = await buy_item(193703684)


async def main():
    logger.info("Старт поллинга бота")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
