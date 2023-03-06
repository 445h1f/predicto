from price_protocols import cryotocompare
import time
from mongo_db import *
import threading


def printPriceEveryTenSeconds(coin:str, currency:str="usd", tillTime:int=5):
    """Prints price of coin/usd every 10 seconds till given minute of time."""
    # api = GeckoAPI()

    tillTime *= 60 # converting  time in seconds

    oldPrice = None
    # running loop while remaining time is greater than 0
    while tillTime > 0:

        # time before calling gecko api to get price
        timeBeforeApiCall = time.time()

        # getting coin price from coingecko api
        price = cryotocompare.getCoinPrice(coin=coin, currency=currency)
        # price = uniswap.getCoinPrice()
        # price = api.getCoinPrice(coinID=coin, currency=currency)

        # assigning emoji with respected price action
        if oldPrice is None or oldPrice == price:
            # no change emoji when price not changes
            emoji = "⏹️"
        elif price > oldPrice:
            # up emoji when price goes up
            emoji = "🔼"
        else:
            # down emoji when price goes down
            emoji = "🔽"

        oldPrice = price # updating old price

        # getting time taken by api call to get result
        timeTakenByApiCall = time.time() - timeBeforeApiCall

        # printing price with remaining time on screen
        print(f'{emoji} ({tillTime}s remaining) : {coin.upper()}/{currency.upper()} {price}')

        # time to sleep
        sleepTime = 10 - timeTakenByApiCall

        if sleepTime > 0:
            time.sleep(sleepTime) # sleeping for needed time seconds
        else:
            tillTime += sleepTime

        tillTime -= 10


class Prediction(PredictoData, PredictoUser):

    COIN_IDS = ["btc", "eth", "bnb", "sol", "doge", "xrp", "ada", "matic"]
    CURRENCIES = ["usd"]
    TIMEFRAMES = [5, 10, 15, 30, 45, 60]

    def __init__(self, userID) -> None:
        self.userID = userID
        # super(PredictoUser, self).__init__(userID)
        PredictoUser.__init__(self, self.userID)
        # super(GeckoAPI, self).__init__()
        # GeckoAPI.__init__(self)
        # super(PredictoData, self).__init__()
        PredictoData.__init__(self)


    def create(self, coin:str, amount:float, currency:str="usd", timeframe:int=2, up:bool=True):
        """Creates higher/lower prediction of coin vs currency for given time."""

        # makiing coin id and currency lower to match the case
        coin = coin.lower()
        currency = currency.lower()

        if coin not in self.COIN_IDS: #checking if coin id is in supported list
            return {"error": "coin not supported."}
        elif currency not in self.CURRENCIES:  #checking if currency is in supported list
            return {"error": "currency not supported"}
        elif timeframe not in self.TIMEFRAMES: # checking if timeframe is in supported list
            return {"error": "invalid time frame"}
        else:
            # all test passed so moving on prediction
            # oldPrice = uniswap.getCoinPrice()
            oldPrice = cryotocompare.getCoinPrice(coin=coin, currency=currency)
            # oldPrice = self.getCoinPrice(coin, currency) #price at which user predicted
            startTime = datetime.now() # prediction time

            direction = 'UP' if up else 'DOWN' # direction of prediction up or down

            print(f'[{startTime:%H:%M:%S}]: {coin}/{currency} = {oldPrice}')
            print(f"You predicted {direction} for upcoming {timeframe} minutes\nLet's see what happens...")

            # prediction data schema
            pairName = f'{coin}/{currency}'.upper()
            data = {
                "from_user" : self.id,
                "pair" : pairName,
                "direction": direction,
                "timeframe" : timeframe,
                "start_time": startTime,
                "start_price": oldPrice,
                "new_price": None,
                "end_time": None,
                "price_change": None,
                "profit": None,
                "status": None,
            }

            # adding prediction db and getting id of stored document
            predictionId = self.addPredictionData(data)

            # adding prediction to user account data
            self.addUserPrediction(pairName=pairName, predictionId=predictionId)

            threading.Thread(target=printPriceEveryTenSeconds, args=[coin, currency, timeframe]).start()

            # time*60 because sleep method takes time in seconds
            time.sleep(timeframe*60)
            endTime = datetime.now()
            # newPrice = self.getCoinPrice(coin, currency)
            # newPrice = uniswap.getCoinPrice()
            newPrice = cryotocompare.getCoinPrice(coin=coin, currency=currency)
            print(f'[{startTime:%H:%M:%S}]: {coin}/{currency} = {newPrice}')

            priceChange = newPrice - oldPrice

            # response data to be sent after prediction
            data["new_price"] = newPrice
            data["price_change"] = priceChange
            data["end_time"] = str(endTime)


            # checking if user won . lose or draw
            if priceChange == 0: # coindtion for draw when price is not changed
                data["status"] = "draw"
                profit = 0
            else:
                # win condition
                if priceChange > 0 and up or priceChange < 0 and not up:
                    data["status"] = "win"
                    profit = amount
                else:
                    data["status"] = "loss"
                    profit = -amount


            data["profit"] = profit

            # updating data after finalizing results
            self.updatePredictionData(id=predictionId, data=data)

            # updating prediction result in user account data
            self.updatePredictionResult(pairName=pairName, status=data["status"], profit=profit)

            # adding prediction id to data for return
            # data["id"] = str(predictionId)

            return data # returning finalized data