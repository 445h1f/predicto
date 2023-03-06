import requests
from dotenv import load_dotenv
import os

# getting cryptocompare API key from .env file
load_dotenv()
API_KEY = os.getenv('CRYPTO_COMPARE_API_KEY')


# endpoint for price
endpoint = 'https://min-api.cryptocompare.com/data/price'

def getCoinPrice(coin:str="btc", currency:str="usd") -> float:
    """Returns price of coin with respect to currency."""

    # url parameters in price url
    params = {
        "fsym": coin,
        "tsyms": currency,
    }

    # adding api key if it is not none
    if API_KEY is not None:
        # adding api key in header
        header = {
            "Authorization" : f"Apikey {API_KEY}"
        }

        # requesting price from api
        r = requests.get(url=endpoint, params=params, headers=header)
    else:
        # requesting without api key
        r = requests.get(url=endpoint, params=params)

    # returning price of coin/currency
    return r.json()[currency.upper()]


if __name__ == "__main__":
    print(getCoinPrice("sol"))

