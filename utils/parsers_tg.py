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
                                   "buyPrice": prices[-1]})
                    return answer

                else:
                    continue


async def namomente_data():
    check_pattern = 'Тарифи уточнюйте в момент операції'
    price_pattern = r'\d+\.\d+ \| \d+\.\d+'
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
                    prices = re.findall(r'\d+\.\d+', 
                                        price_match)
                    answer.update({"exchanger": exchanger,
                                   "url": url,
                                   "buyPrice": float(prices[1])})
                    return answer
                else:
                    continue


async def valuta_data():
    check_pattern = 'Курс дійсний протягом 1 години.'
    usd_pattern = r"USD:\s+\d+\.\d+ / (\d+\.\d+)"
    usdt_pattern = r"/\s*([+-]?\d+(?:\.\d+)?)\s*%"
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
                            str(message))
                    usdt_matches = re.findall(
                            usdt_pattern, 
                            str(message))
                    usd_price = float(usd_matches[0])
                    usdt_percent_price = float(usdt_matches[0])
                    buy_price = Decimal(usd_price) + (
                            Decimal(usdt_percent_price
                                    ) / 100 * Decimal(usd_price))
                    buy_price = float('{:.3f}'.format(buy_price))
                    answer.update({"exchanger": exchanger,
                                   "url": url,
                                   "buyPrice": buy_price})
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
    asyncio.run(master_parser())
