from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Начать отслеживание")],
            [KeyboardButton(text="⚙️ Фильтры")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

def resale_button(item_id: int, price: float):
    return InlineKeyboardMarkup(
        keyboard=[
            InlineKeyboardButton(text="🔁 Перепродать",
                                 callback_data=f"resell:{item_id}:{price}"
                                 )
        ]
    )