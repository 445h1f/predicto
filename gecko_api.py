import requests
import json

class GeckoAPI:

    root = "https://api.coingecko.com/api/v3/"

    def __init__(self):
        self.session = requests.Session()

    def ping(self):
        endpoint = f"{self.root}/ping"
        r = self.session.get(endpoint)
        return r.json()

    def allCoinsList(self):
        endpoint = f'{self.root}/coins/list'
        r = self.session.get(endpoint)
        r.raise_for_status()
        return r.json()

    def coinsByCategory(self, category:str=None):
        categories = [
            "market_cap_desc",
            "market_cap_asc",
            "name_desc",
            "name_asc",
            "market_cap_change_24h_desc",
            "market_cap_change_24h_asc"
        ]

        f"""Returns coins list with provided category. Categories: {",".join([i for i in categories])}"""


        endpoint = f'{self.root}/coins/categories'

        if category is None or category not in categories:
            # returns data from default category is category is none or not a valid one
            r = self.session.get(endpoint)
        else:
            # if category is valid the getting data of given catgeory
            query = {"order": category}
            r = self.session.get(endpoint, params=query)
        r.raise_for_status()
        return r.json()


    def getSupportedCurrencies(self):
        """Returns supported currencies data."""

        endpoint = f"{self.root}/simple/supported_vs_currencies"
        r = self.session.get(url=endpoint)
        r.raise_for_status()
        return r.json()


    def getCoinPrice(self, coinID:str, currency:str="usd", precison:int=5):
        """Returns price of given coin id."""
        query = {
                "ids": coinID.lower(),
                "vs_currencies": currency.lower(),
                "precision": precison,
            }
        endpoint = f"{self.root}/simple/price"
        r = self.session.get(url=endpoint, params=query)
        r.raise_for_status()
        return r.json()[coinID][currency]


if __name__ == "__main__":
    api = GeckoAPI()
    print(api.getSupportedCurrencies())
    # print(api.getCoinPrice("bitcoin", "usd"))
    # print(api.coinsByCategory("market_cap_change_24h_desc"))
