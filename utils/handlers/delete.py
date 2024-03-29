from aiogram import F, Router, types


delete_router = Router()


@delete_router.callback_query(F.data == "delete_message")
async def delete_message(cb: types.CallbackQuery):
    await cb.answer()
    if not isinstance(cb.message, 
                      types.InaccessibleMessage) and cb.message:
        await cb.message.delete()
