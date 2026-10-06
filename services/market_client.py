from LOLZTEAM.Client import Market
from config import LOLZ_API_TOKEN
import logging
from services.utils import save_to_json_default
import asyncio

logger = logging.getLogger(__name__)
market = Market(LOLZ_API_TOKEN)

# async def get_fortnite_accounts():
#     try:
#         logger.debug("Запрос Fortnite аккаунтов (pmin=0, pmax=200)")
#         response = await market.categories.fortnite.get(
#             pmin=0,
#             pmax=200,
#         )

#         data = response.json()
#         items = data.get("items", [])
#         # logger.info("Получено Fortnite аккаунтов: %d", len(items))
#         return items
#     except Exception as e:
#         logger.exception("Ошибка при получении Fortnite аккаунтов")
#         return []


async def get_fortnite_accounts():
    try:
        logger.debug("Запрос Fortnite аккаунтов (pmin=0, pmax=200)")
        response = await market.categories.fortnite.get(
            pmin=0,
            pmax=200,
        )

        data = response.json()
        # save_to_json_default(data, "fort.json")
        items = data.get("items", [])
        logger.info("Получено Fortnite аккаунтов: %d", len(items))
        return items
    except Exception as e:
        logger.exception("Ошибка при получении Fortnite аккаунтов")
        return []


async def get_epicgames_accounts():
    try:
        logger.debug("Запрос EpicGames аккаунтов (pmin=0, pmax=200)")
        response = await market.categories.epicgames.get(
            pmin=0,
            pmax=200,
        )
        data = response.json()
        items = data.get("items", [])
        logger.info("Получено EpicGames аккаунтов: %d", len(items))
        return items
    except Exception as e:
        logger.exception("Ошибка при получении EpicGames аккаунтов")
        return []


async def buy_item(item_id: int, price: float):
    try:
        logger.info("Покупка товара item_id=%s по цене=%s", item_id, price)
        response = await market.purchasing.fast(item_id=item_id, price=price)

        data = response.json()
        status = data.get("status")

        if status == "ok":
            logger.info("Покупка успешна item_id=%s", item_id)
            return True
        else:
            logger.warning("Ошибка покупки item_id=%s, ответ=%s", item_id, data)
            return False
    except Exception:
        logger.exception("Исключение при покупке item_id=%s", item_id)
        return False
