import asyncio
import logging
import json
from pathlib import Path

from services.market_client import (
    get_fortnite_accounts,
    get_epicgames_accounts,
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
            # Параллельный запрос обеих категорий
            fortnite_accounts, epicgames_accounts = await asyncio.gather(
                get_fortnite_accounts(),
                get_epicgames_accounts(),
                return_exceptions=True,
            )

            # Обработка ошибок gather
            if isinstance(fortnite_accounts, Exception):
                logger.error("Ошибка получения Fortnite: %s", fortnite_accounts)
                fortnite_accounts = []
            if isinstance(epicgames_accounts, Exception):
                logger.error("Ошибка получения Epic Games: %s", epicgames_accounts)
                epicgames_accounts = []

            logger.debug(
                "Получено %d Fortnite + %d Epic Games аккаунтов",
                len(fortnite_accounts),
                len(epicgames_accounts),
            )

            all_accounts = [
                ("Fortnite", fortnite_accounts),
                ("Epic Games", epicgames_accounts),
            ]

            for category_name, accounts in all_accounts:
                for acc in accounts:
                    acc_id = acc["item_id"]

                    if acc_id in sent_ids:
                        continue

                    # Поиск DBD в зависимости от категории
                    if category_name == "Fortnite":
                        transactions = acc.get("fortniteTransactions", [])
                        has_dbd = any(
                            "dead by daylight" in tx.get("title", "").strip().lower()
                            for tx in transactions
                        )
                    else:  # Epic Games
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
                                )
                                logger.warning("Покупка неуспешна id=%s", acc_id)
                            await bot.send_message(chat_id, msg)

        except Exception as e:
            logger.exception("💥 Ошибка в процессе оповещения")

        await asyncio.sleep(interval)
