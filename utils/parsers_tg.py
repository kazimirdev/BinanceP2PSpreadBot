import asyncio
import re
import aiohttp
import bs4 

from decimal import Decimal


async def menora_data():
    check_pattern = 'Купуємо тезер'
    price_pattern = r'\b\d+\.\d+\b'
     
    exchanger = "Menora_Crypto"
    url = f"https://t.me/s/{exchanger}"
    answer = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = bs4.BeautifulSoup(html, 
                                     features="html.parser")
            messages = soup.find_all("div", 
                                     "tgme_widget_message_text js-message_text")
            messages = reversed(messages)
            for message in messages:
                check_match = re.search(check_pattern, 
                                        str(message))
                if check_match:
                    price_match = re.findall(price_pattern, 
                                             str(message))
                    prices = [float(price) for price in price_match]
                    answer.update({"exchanger": exchanger,
                                   "url": url,
                                   "buyPrice": prices[-1],
                                   "sellPrice": prices[1]})
                    return answer

                else:
                    continue


async def namomente_data():
    check_pattern = 'Тарифи уточнюйте в момент операції'
    price_pattern = r'(\d+\.\d+)\s*\|\s*(\d+\.\d+)'
    exchanger = "namomente_crypto"
    url = f"https://t.me/s/{exchanger}"
    answer = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = bs4.BeautifulSoup(html, 
                                     features="html.parser")
            messages = soup.find_all("div", 
                                     "tgme_widget_message_text js-message_text")
            messages = reversed(messages)
            for message in messages:
                check_match = re.search(check_pattern, 
                                        str(message))
                if check_match:
                    price_match = re.findall(price_pattern, 
                                             str(message))[0]
                    answer.update({"exchanger": exchanger,
                                   "url": url,
                                   "buyPrice": float(price_match[1]),
                                   "sellPrice": float(price_match[0])})
                    return answer
                else:
                    continue


async def valuta_data():
    check_pattern = 'Курс дійсний протягом 1 години.'
    usd_pattern = r"USD:\s*([\d,\.]+)\s*/\s*([\d,\.]+)"
    usdt_pattern = r"USDT:\s*([+-]?\d+(?:\.\d+)?)%?\s*/\s*([+-]?\d+(?:\.\d+)?)%?"
    exchanger = "valuta_Dp_opt"
    url = f"https://t.me/s/{exchanger}"
    answer = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = bs4.BeautifulSoup(html, 
                                     features="html.parser")
            messages = soup.find_all("div", 
                                     "tgme_widget_message_text js-message_text")
            messages = reversed(messages)
            for message in messages:
                check_match = re.search(check_pattern, 
                                        str(message))
                if check_match:
                    usd_matches = re.findall(
                            usd_pattern, 
                            str(message))[0]
                    usdt_matches = re.findall(
                            usdt_pattern, 
                            str(message))[0]
                    usd_sell_price = usd_matches[0]
                    usdt_sell_percent = usdt_matches[0]
                     
                    usd_sell_price = usd_matches[0]
                    usdt_sell_percent = usdt_matches[0]
                    uah_to_usdt_price = float(Decimal(usd_sell_price) + (
                            Decimal(usdt_sell_percent
                                    ) / 100 * Decimal(usd_sell_price)))

                    usd_buy_price = usd_matches[-1]
                    usdt_buy_percent = usdt_matches[-1]
                    usd_to_uah_price = float(Decimal(usd_buy_price) + (
                            Decimal(usdt_buy_percent
                                    ) / 100 * Decimal(usd_buy_price)))
                    answer.update({"exchanger": exchanger,
                                   "url": url,
                                   "buyPrice": usd_to_uah_price,
                                   "sellPrice": uah_to_usdt_price})
                    return answer
                else:
                    continue


async def master_parser() -> tuple[dict, dict, dict]:
    parsers = [menora_data, namomente_data, valuta_data]
    response = []
    for parser in parsers:
        await asyncio.sleep(0.5)
        data = await parser()
        response.append(data)
    menora, namomente, valuta = response
    return menora, namomente, valuta


if __name__ == "__main__":
    print(asyncio.run(menora_data()))
    print(asyncio.run(namomente_data()))
    print(asyncio.run(valuta_data()))
