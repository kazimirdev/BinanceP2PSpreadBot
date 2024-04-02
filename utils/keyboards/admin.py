from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Обновить данные",
        callback_data="update_start"))
    builder.row(InlineKeyboardButton(
        text="Купить на Binance, продать в обменнике",
        callback_data="update_spread_limit_buy_binance_sell_exchanger"))
    builder.row(InlineKeyboardButton(
        text="Купить в обменнике, продать на Binance",
        callback_data="update_spread_limit_buy_exchanger_sell_binance"))
    return builder.as_markup()


def update_spread_limit(is_correct: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    button_text = "Вернуться к данным" if is_correct else "Отмена изменений"
    builder.row(InlineKeyboardButton(
        text=button_text,
        callback_data="update_start"))
    return builder.as_markup()

