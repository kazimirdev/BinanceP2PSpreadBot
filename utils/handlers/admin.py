from decimal import Decimal

from aiogram import F, Bot, Router, types, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types.link_preview_options import LinkPreviewOptions
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils import keyboards, parsers_tg, parsers_binance, states
from utils.config import load_config
from utils.filters.admin import AdminFilter


admin_router = Router()
admin_router.message.filter(AdminFilter())

bot = Bot(token=load_config().tgbot.token) 

@admin_router.message(CommandStart())
@admin_router.callback_query(F.data == "update_start")
async def start_msg(event: types.Message|types.CallbackQuery,
                    state: FSMContext):
    binance = await parsers_binance.usdt_to_uah()
    binance_sell_price = binance["sellPrice"]
    binance_seller_name = binance["nickName"]
    binance_seller_link = binance["link"]
    binance_seller_hlink = html.link(value=binance_seller_name,
                                     link=binance_seller_link)
    binance_min_limit = binance["minSingleTransAmount"]
    binance_max_limit = binance["maxSingleTransAmount"]

    keyboard = keyboards.admin.start()
    msg_text = f"""
Лучшее предложение на Binance:
USDT → UAH: {binance_sell_price} UAH
Продавец: {binance_seller_hlink}
Лимиты: {binance_min_limit}-{binance_max_limit} UAH

"""
    parsers = await parsers_tg.master_parser()
    
    for parser in parsers:
        parser_buy_price = parser["buyPrice"]
        parser_name = parser["exchanger"]
        parser_link = parser["url"]
        parser_hlink = html.link(value=parser_name,
                                 link=parser_link)

        msg_text += f"""
{parser_hlink}:
UAH → USDT: {parser_buy_price} UAH
Спред за 1 единицу: {float('{:.4f}'.format(Decimal(binance_sell_price) - Decimal(parser_buy_price)))} UAH
        """

    await state.set_state(states.admin.SpreadLimit.UsingData)
    state_data = await state.get_data()
    spread_limit = state_data.get("spread_limit")
    msg_text += f"""
Лимит спреда: {spread_limit or "0 (уведомления отключены)"}"""
    if isinstance(event,
                  types.CallbackQuery
                  ) and not isinstance(event.message,
                                       types.InaccessibleMessage
                                       ) and event.message:
        await event.answer()
        try:
            await event.message.edit_text(text=msg_text,
                                          reply_markup=keyboard,
                                          link_preview_options=LinkPreviewOptions(
                                              is_disabled=True))
        except TelegramBadRequest:
            pass
    else:
        await event.answer(text=msg_text,
                           reply_markup=keyboard,
                           link_preview_options=LinkPreviewOptions(
                               is_disabled=True))
    

@admin_router.callback_query(F.data == "update_spread_limit")
async def update_spread_limit(cb: types.CallbackQuery,
                              state: FSMContext):
    if not isinstance(cb.message, 
                      types.InaccessibleMessage) and cb.message:
        await cb.answer()
        state_data = await state.get_data()
        spread_limit = state_data.get("spread_limit")
        keyboard = keyboards.admin.update_spread_limit()
        msg_text = f"""
Текущий лимит спреда {spread_limit or 0}
Введите лимит спреда что бы включить уведомления. 
Введите 0 что бы выключить уведомления.

Примеры ввода: 1 .5 0.5 1.55 (одним числом без пробелов)
"""
        bot_msg = await cb.message.edit_text(
                text=msg_text,
                reply_markup=keyboard,
                link_preview_options=LinkPreviewOptions(
                    is_disabled=True))
        if isinstance(bot_msg, types.Message):
            await state.set_state(
                    states.admin.SpreadLimit.UpdatingData)
            await state.update_data(
                    {"bot_message_id": bot_msg.message_id})


@admin_router.message(states.admin.SpreadLimit.UpdatingData)
async def check_updated_spread_limit(msg: types.Message,
                                     state: FSMContext,
                                     scheduler:  AsyncIOScheduler):
    await msg.delete()
    if msg.text and msg.from_user:
        user_id = msg.from_user.id
        state_data = await state.get_data()
        bot_message_id = state_data["bot_message_id"]

        try:
            spread_limit = float(msg.text)
            job_id = f"send_notification:user_id={msg.from_user.id}"
            try:
                scheduler.remove_job(job_id=job_id)
            except JobLookupError:
                pass
            if spread_limit != 0:
                scheduler.add_job(send_notification, 
                                  "interval", 
                                  seconds=3.5,
                                  id=job_id,
                                  kwargs={"user_id": user_id,
                                          "spread_limit": spread_limit})
            msg_text = f"Данные обновлены, спред равен {spread_limit}."
            is_correct = True
            await state.update_data({"spread_limit": spread_limit})
            await state.set_state(states.admin.SpreadLimit.UsingData)
        except ValueError as e:
            msg_text = f"Неправильно введены данные, попробуйте ещё раз...\n{e}"
            is_correct = False
        keyboard = keyboards.admin.update_spread_limit(is_correct)
        await bot.edit_message_text(
                chat_id=msg.chat.id,
                message_id=bot_message_id,
                text=msg_text,
                reply_markup=keyboard,
                link_preview_options=LinkPreviewOptions(
                    is_disabled=True))


async def send_notification(bot: Bot,
                            user_id: int,
                            spread_limit: float):
    binance = await parsers_binance.usdt_to_uah()
    keyboard = keyboards.delete.message_inline()
    tg_parsers = await parsers_tg.master_parser()
    
    bin_sell_price = float(binance["sellPrice"])
    bin_name = binance["nickName"]
    bin_link = binance["link"]
    bin_hlink = html.link(value=bin_name,
                          link=bin_link)   
    msg_text = ""
    for parser in tg_parsers:
        if spread_limit <= Decimal(bin_sell_price) - Decimal(
                parser["buyPrice"]):
            parser_hlink = html.link(value=parser["exchanger"],
                                     link=parser["url"])
            msg_text += f"""
TG: {parser_hlink}:
UAH → USDT: {parser["buyPrice"]}
Спред: {float('{:.4f}'.format(Decimal(bin_sell_price) - Decimal(parser["buyPrice"])))}"""
    if msg_text:
        msg_text = f"""
Предллжения спреда выше минимального! ({spread_limit} UAH) 
Binance: {bin_hlink}, USDT → UAH: {bin_sell_price}
""" + msg_text
    try:
        await bot.send_message(chat_id=user_id,
                               text=msg_text,
                               reply_markup=keyboard)
    except TelegramBadRequest:
        pass

