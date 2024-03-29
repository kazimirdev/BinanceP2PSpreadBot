from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def message_inline():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Удалить сообщение",
        callback_data="delete_message"))
    return builder.as_markup()
