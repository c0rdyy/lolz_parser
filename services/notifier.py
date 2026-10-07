import asyncio
import logging

from services.market_client import (
    buy_item,
    get_latest_accounts,
)

logger = logging.getLogger(__name__)


async def notify_new_accounts(bot, chat_id: int, interval: int):
    logger.info("Запущен цикл отслеживания: chat_id=%s, interval=%s", chat_id, interval)

    while True:
        try:
            accounts = await get_latest_accounts()

            if isinstance(accounts, Exception):
                logger.error("Ошибка получения аккаунтов: %s", accounts)
                accounts = []

            logger.debug("Получено %d аккаунтов из latest", len(accounts))

            for acc in accounts:
                acc_id = acc["item_id"]

                category_name = "Epic games"

                has_dbd = False

                transactions = acc.get("fortniteTransactions") or []

                has_dbd = any(
                    "dead by daylight" in tx.get("title", "").strip().lower()
                    for tx in transactions
                    if isinstance(tx, dict)
                )

                epicgames_games = acc.get("epicgames_games") or []

                if isinstance(epicgames_games, dict):
                    games = epicgames_games.values()
                elif isinstance(epicgames_games, list):
                    games = epicgames_games
                else:
                    games = []

                has_dbd = has_dbd or any(
                    "dead by daylight" in game.get("title", "").strip().lower()
                    for game in games
                    if isinstance(game, dict)
                )

                if has_dbd:
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
                                f"💰 Цена: {acc['price']}₽\n"
                                f"🔗 Ссылка: https://lzt.market/{acc_id}"
                            )
                            logger.warning("Покупка неуспешна id=%s", acc_id)
                        await bot.send_message(chat_id, msg)

        except Exception as e:
            logger.exception("💥 Ошибка в процессе оповещения")

        await asyncio.sleep(interval)
