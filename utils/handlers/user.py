from aiogram import Router, types
from aiogram.filters import CommandStart


user_router = Router()


@user_router.message(CommandStart())
async def start_msg(msg: types.Message):
    await msg.reply(text=f"""
Этот бот написан не для тебя и не для таких как ты!
По всем вопросам к @kazimirdev.
Твой TID: {msg.from_user.id if msg.from_user else "Не установлен"}
""")
