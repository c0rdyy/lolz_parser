import json
import logging

logger = logging.getLogger(__name__)


def extract_useful_data(account):
    return {
        "id": account["item_id"],
        "title": account["title"],
        "price": account["price"],
        "level": account.get("fortnite_level"),
        "balance": account.get("fortnite_balance"),
        "skin_count": account.get("fortnite_skin_count"),
        "transactions": [
            {"title": purchase["title"]}
            for purchase in account.get("fortniteTransactions", [])
        ],
        "link": f"https://lzt.market/{account['item_id']}",
    }


def save_to_json(data, filename):
    filtered_data = [extract_useful_data(acc) for acc in data]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Данные сохранены в файл: {filename}")


def save_to_json_default(data, filename):

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"✅ Данные сохранены в файл: {filename}")
