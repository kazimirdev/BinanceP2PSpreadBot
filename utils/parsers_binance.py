import asyncio
import aiohttp

async def usdt_to_uah(): 
    data = {
    "fiat": "UAH",
    "page": 1,
    "rows": 10,
    "tradeType": "SELL",
    "asset": "USDT",
    "countries": [],
    "proMerchantAds": False,
    "shieldMerchantAds": False,
    "filterType": "all",
    "additionalKycVerifyFilter": 0,
    "payTypes": ["ABank", "Monobank", "PrivatBank",  "PUMBBank"],
    }
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json() 
            ads = result['data']
            ad = ads[0]
            advNo = ad['adv']['advNo']
            output = {
                "tradableQuantity": ad['adv']['tradableQuantity'],
                "sellPrice": ad['adv']['price'],
                "nickName": ad['advertiser']['nickName'],
                "tradeType": ad['adv']['tradeType'],
                "minSingleTransAmount": ad['adv']['minSingleTransAmount'],
                "maxSingleTransAmount": ad['adv']['maxSingleTransAmount'],
                "tradeMethodName" : ', '.join(
                    [tmethods['tradeMethodName'
                    ] for tmethods in ad['adv'
                                        ]['tradeMethods'
                                         ] if tmethods['tradeMethodName']]),
                "link": f"https://p2p.binance.com/uk/advertiserDetail?advertiserNo={advNo}"
                }
        return output


async def uah_to_usdt(): 
    data = {
    "fiat": "UAH",
    "page": 1,
    "rows": 10,
    "tradeType": "BUY",
    "asset": "USDT",
    "countries": [],
    "proMerchantAds": False,
    "shieldMerchantAds": False,
    "filterType": "all",
    "additionalKycVerifyFilter": 0,
    "payTypes": ["ABank", "Monobank", "PrivatBank",  "PUMBBank"],
    }
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json() 
            ads = result['data']
            ad = ads[0]
            advNo = ad['adv']['advNo']
            output = {
                "tradableQuantity": ad['adv']['tradableQuantity'],
                "buyPrice": ad['adv']['price'],
                "nickName": ad['advertiser']['nickName'],
                "tradeType": ad['adv']['tradeType'],
                "minSingleTransAmount": ad['adv']['minSingleTransAmount'],
                "maxSingleTransAmount": ad['adv']['maxSingleTransAmount'],
                "tradeMethodName" : ', '.join(
                    [tmethods['tradeMethodName'
                    ] for tmethods in ad['adv'
                                        ]['tradeMethods'
                                         ] if tmethods['tradeMethodName']]),
                "link": f"https://p2p.binance.com/uk/advertiserDetail?advertiserNo={advNo}"
                }
        return output

if __name__ == '__main__':
    print(asyncio.run(usdt_to_uah()))
    print(asyncio.run(uah_to_usdt()))
