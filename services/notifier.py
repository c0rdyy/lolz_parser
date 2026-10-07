import asyncio
import logging
import json
from pathlib import Path

from services.market_client import (
    get_latest_accounts,
    buy_item,
)

logger = logging.getLogger(__name__)

SENT_IDS_FILE = Path(__file__).parent.parent / "sent_ids.json"


def load_sent_ids():
    try:
        with open(SENT_IDS_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        logger.info("Файл sent_ids.json не найден, создаётся новый")
        return set()
    except Exception as e:
        logger.exception("Ошибка загрузки sent_ids.json")
        return set()


def save_sent_ids(ids):
    try:
        with open(SENT_IDS_FILE, "w") as f:
            json.dump(list(ids), f)
    except Exception as e:
        logger.exception("Ошибка сохранения sent_ids.json")


sent_ids = load_sent_ids()


async def notify_new_accounts(bot, chat_id: int, interval: int):
    logger.info("Запущен цикл отслеживания: chat_id=%s, interval=%s", chat_id, interval)

    while True:
        try:
            # Один запрос вместо двух — быстрее в 2 раза
            accounts = await get_latest_accounts()

            if isinstance(accounts, Exception):
                logger.error("Ошибка получения аккаунтов: %s", accounts)
                accounts = []

            logger.debug("Получено %d аккаунтов из latest", len(accounts))

            for acc in accounts:
                acc_id = acc["item_id"]

                if acc_id in sent_ids:
                    continue

                # Определяем категорию по category_id
                category_id = acc.get("category_id")

                # Fortnite: category_id = 7
                # Epic Games: category_id = 12
                if category_id == 7:
                    category_name = "Fortnite"
                    transactions = acc.get("fortniteTransactions", [])
                    has_dbd = any(
                        "dead by daylight" in tx.get("title", "").strip().lower()
                        for tx in transactions
                    )
                elif category_id == 12:
                    category_name = "Epic Games"
                    epicgames_games = acc.get("epicgames_games", {})
                    if isinstance(epicgames_games, dict):
                        games_list = list(epicgames_games.values())
                    elif isinstance(epicgames_games, list):
                        games_list = epicgames_games
                    else:
                        games_list = []

                    has_dbd = any(
                        "dead by daylight" in game.get("title", "").strip().lower()
                        for game in games_list
                        if isinstance(game, dict)
                    )
                else:
                    # Пропускаем другие категории
                    continue

                if has_dbd:
                    sent_ids.add(acc_id)
                    save_sent_ids(sent_ids)
                    logger.info(
                        "Найден подходящий аккаунт id=%s, category=%s, price=%s",
                        acc_id,
                        category_name,
                        acc.get("price"),
                    )

                    if acc["price"] <= 50:
                        success = await buy_item(acc_id, acc["price"])
                        if success:
                            await bot.send_message(
                                chat_id, "✅ Аккаунт успешно куплен!"
                            )
                            msg = (
                                f"🕹️ Куплен аккаунт из категории {category_name}\n"
                                f"📦 {acc['title']}\n"
                                f"💰 Цена: {acc['price']}₽\n"
                                f"🔗 Ссылка: https://lzt.market/{acc_id}"
                            )
                            logger.info("Покупка успешна id=%s", acc_id)
                        else:
                            msg = (
                                f"❌ Не удалось купить аккаунт!\n"
                                f"📦 {acc['title']}\n"
                                f"💰 Цена: {acc['price']}₽"
                                f"🔗 Ссылка: https://lzt.market/{acc_id}"
                            )
                            logger.warning("Покупка неуспешна id=%s", acc_id)
                        await bot.send_message(chat_id, msg)

        except Exception as e:
            logger.exception("💥 Ошибка в процессе оповещения")

        await asyncio.sleep(interval)
