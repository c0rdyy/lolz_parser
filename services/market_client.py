import logging

from LOLZTEAM.Client import Market

from config import LOLZ_API_TOKEN

logger = logging.getLogger(__name__)

market = Market(LOLZ_API_TOKEN, delay_min=0)


async def get_latest_accounts():
    """
    Получить последние аккаунты из всех категорий одним запросом.
    """
    try:
        logger.debug("Запрос последних аккаунтов (pmin=0, pmax=100)")
        response = await market.categories.epicgames.get(
            pmin=0,
            pmax=100,
        )

        data = response.json()
        items = data.get("items", [])
        logger.info("Получено аккаунтов из latest: %d", len(items))
        return items
    except Exception as e:
        logger.exception("Ошибка при получении latest аккаунтов")
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
