import asyncio
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
    keyboard = keyboards.admin.start()
    msg_text = f"Лучшия предложения на Binance:"
    binance_uah_to_usdt = await parsers_binance.uah_to_usdt()
    binance_buy_amount = binance_uah_to_usdt["tradableQuantity"]
    binance_buy_price = binance_uah_to_usdt["buyPrice"]
    binance_buy_name = binance_uah_to_usdt["nickName"]
    binance_buy_link = binance_uah_to_usdt["link"]
    binance_buy_hlink = html.link(value=binance_buy_name,
                                  link=binance_buy_link)
    binance_min_buy_limit = binance_uah_to_usdt["minSingleTransAmount"]
    binance_max_buy_limit = binance_uah_to_usdt["maxSingleTransAmount"]

    msg_text += f"""
UAH → USDT: {binance_buy_price} UAH
Продавец: {binance_buy_hlink or binance_buy_link}
Доступно на обмен: {binance_buy_amount} USDT
Лимиты: {binance_min_buy_limit}-{binance_max_buy_limit} UAH
"""
    
    binance_usdt_to_uah = await parsers_binance.usdt_to_uah()
    binance_sell_tradable_quantity = binance_usdt_to_uah["tradableQuantity"]
    binance_sell_price = binance_usdt_to_uah["sellPrice"]
    binance_sell_name = binance_usdt_to_uah["nickName"]
    binance_sell_link = binance_usdt_to_uah["link"]
    binance_sell_hlink = html.link(value=binance_sell_name,
                                     link=binance_sell_link)
    binance_min_sell_limit = binance_usdt_to_uah["minSingleTransAmount"]
    binance_max_sell_limit = binance_usdt_to_uah["maxSingleTransAmount"]
    msg_text += f"""
USDT → UAH: {binance_sell_price} UAH
Продавец: {binance_sell_hlink}
Доступно на обмен: {binance_sell_tradable_quantity} USDT
Лимиты: {binance_min_sell_limit}-{binance_max_sell_limit} UAH
"""
    
    parsers = await parsers_tg.master_parser()
    
    for parser in parsers:
        parser_buy_price = parser["buyPrice"]
        parser_sell_price = parser["sellPrice"]
        parser_name = parser["exchanger"]
        parser_link = parser["url"]
        parser_hlink = html.link(value=parser_name,
                                 link=parser_link)

        msg_text += f"""
{parser_hlink}:
USDT → UAH: {parser_sell_price} UAH
UAH → USDT: {parser_buy_price} UAH
1 спреда за USDT → UAH: {float('{:.4f}'.format(Decimal(str(parser_sell_price)) - Decimal(str(binance_buy_price))))} UAH
1 cпреда за UAH → USDT: {float('{:.4f}'.format(Decimal(str(binance_sell_price)) - Decimal(str(parser_buy_price))))} UAH
"""

    await state.set_state(states.admin.SpreadLimit.UsingData)
    state_data = await state.get_data()
    spread_limit_buy_exchanger_sell_binance = state_data.get("spread_limit_buy_exchanger_sell_binance")
    spread_limit_buy_binance_sell_exchanger = state_data.get("spread_limit_buy_binance_sell_exchanger")
    msg_text += f"""
Лимиты:
"UAH → Binance → USDT → Обменник → UAH": {spread_limit_buy_binance_sell_exchanger or "0 (без уведомлений)"}
"UAH → Обменник → USDT → Binance → UAH": {spread_limit_buy_exchanger_sell_binance or "0 (без уведомлений)"}"""
    if isinstance(event,
                  types.CallbackQuery
                  ) and not isinstance(event.message,
                                       types.InaccessibleMessage
                                       ) and event.message:
        await event.answer()
        try:
            user_id = event.from_user.id
            bot_message =await event.message.edit_text(
                    text=msg_text,
                    reply_markup=keyboard,
                    link_preview_options=LinkPreviewOptions(
                    is_disabled=True))
        except TelegramBadRequest:
            return
    else:
        user_id = event.from_user.id
        bot_message = await event.answer(
                text=msg_text,
                reply_markup=keyboard,
                link_preview_options=LinkPreviewOptions(
                is_disabled=True))
    await bot.pin_chat_message(chat_id=user_id,
                               message_id=bot_message.message_id,
                               disable_notification=True)


@admin_router.callback_query(
        F.data == "update_spread_limit_buy_exchanger_sell_binance")
@admin_router.callback_query(
        F.data == "update_spread_limit_buy_binance_sell_exchanger")
async def update_spread_limit(cb: types.CallbackQuery,
                              state: FSMContext):
    if not isinstance(cb.message, 
                      types.InaccessibleMessage) and cb.message:
        await cb.answer()
        match cb.data:
            case "update_spread_limit_buy_exchanger_sell_binance": 
                spread_key = "spread_limit_buy_exchanger_sell_binance"
                spread_text = "USDT → UAH"
            case "update_spread_limit_buy_binance_sell_exchanger":
                spread_key = "spread_limit_buy_binance_sell_exchanger"
                spread_text = "UAH → USDT"
            case _:
                raise Exception
        state_data = await state.get_data()
        spread_limit = state_data.get(spread_key)
        keyboard = keyboards.admin.update_spread_limit()
        msg_text = f"""
Текущий лимит спреда {spread_limit or 0} для {spread_text}
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
            await state.set_state(states.admin.SpreadLimit.UpdatingLimit)
            await state.update_data(
                    {"bot_message_id": bot_msg.message_id,
                     "spread_key": spread_key,
                     "spread_text": spread_text})


@admin_router.message(states.admin.SpreadLimit.UpdatingLimit)
async def check_updated_uah_to_usdt_spread_limit(
        msg: types.Message,
        state: FSMContext,
        scheduler:  AsyncIOScheduler):
    await msg.delete()
    if msg.text and msg.from_user:
        user_id = msg.from_user.id
        state_data = await state.get_data()
        bot_message_id = state_data["bot_message_id"]

        try:
            spread_limit = float(msg.text)
            spread_key = state_data["spread_key"]
            match spread_key:
                case "spread_limit_buy_exchanger_sell_binance":
                    job = buy_exchanger_sell_binance_notification
                case "spread_limit_buy_binance_sell_exchanger":
                    job = buy_binance_sell_exchanger_notification
                case _:
                    await msg.answer(text=f"{spread_key=}")
                    raise Exception
            spread_text = state_data["spread_text"]
            job_id = f"send_notification:type={spread_key}:user_id={msg.from_user.id}"
            try:
                scheduler.remove_job(job_id=job_id)
            except JobLookupError:
                pass
            if spread_limit != 0:
                scheduler.add_job(job, 
                                  "interval", 
                                  seconds=3.5,
                                  id=job_id,
                                  kwargs={"user_id": user_id,
                                          "spread_limit": spread_limit})
            msg_text = f"Данные обновлены, спред для {spread_text} равен {spread_limit}."
            is_correct = True
            await state.update_data({spread_key: spread_limit})
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


async def buy_exchanger_sell_binance_notification(bot: Bot,
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
        if spread_limit <= (Decimal(str(bin_sell_price)) - Decimal(str(parser["buyPrice"]))):
            parser_hlink = html.link(value=parser["exchanger"],
                                     link=parser["url"])
            msg_text += f"""
TG: {parser_hlink}:
UAH → USDT: {parser["buyPrice"]}
Спред UAH → USDT → Binance: {Decimal(str(bin_sell_price)) - Decimal(str(parser["buyPrice"]))}"""
    if msg_text:
        msg_text = f"""
Купить в обменнике, продать на Binance:
Предложения спреда выше минимального! ({spread_limit} UAH) 
Binance: {bin_hlink or bin_link}, USDT → UAH: {bin_sell_price}
""" + msg_text
    try:
       bot_message = await bot.send_message(chat_id=user_id,
                                            text=msg_text,
                                            reply_markup=keyboard)
       await asyncio.sleep(10)
       await bot_message.delete()
    except TelegramBadRequest:
        pass


async def buy_binance_sell_exchanger_notification(bot: Bot,
                                                  user_id: int,
                                                  spread_limit: float):

    binance = await parsers_binance.uah_to_usdt()
    keyboard = keyboards.delete.message_inline()
    tg_parsers = await parsers_tg.master_parser()
    
    bin_sell_price = float(binance["buyPrice"])
    bin_name = binance["nickName"]
    bin_link = binance["link"]
    bin_hlink = html.link(value=bin_name,
                          link=bin_link)   
    msg_text = ""
    for parser in tg_parsers:
        if spread_limit <= (Decimal(str(parser["sellPrice"])) - Decimal(str(bin_sell_price))):
            parser_hlink = html.link(value=parser["exchanger"],
                                     link=parser["url"])
            msg_text += f"""
TG: {parser_hlink}:
USDT → UAH: {parser["sellPrice"]}
Спред UAH → USDT → Binance: {Decimal(str(parser["sellPrice"])) - Decimal(str(bin_sell_price))}"""
    if msg_text:
        msg_text = f"""
Купить на Binance, продать в обменнике
Предложения спреда выше минимального! ({spread_limit} UAH) 
Binance: {bin_hlink or bin_link}, USDT → UAH: {bin_sell_price}
""" + msg_text
    try:
       bot_message = await bot.send_message(chat_id=user_id,
                                            text=msg_text,
                                            reply_markup=keyboard)
       await asyncio.sleep(10)
       await bot_message.delete()
    except TelegramBadRequest:
        pass
