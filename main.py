from predict import *


if __name__ == "__main__":
    predict = Prediction(100000001)

    # printing all supported coins
    for index, coin in enumerate(predict.COIN_IDS):
        print(f'{index+1}. {coin.upper()}')

    # asking coin from user
    coin = input("Enter coin from above menu: ").lower()

    # checking if coin is in supported coin list
    if coin in predict.COIN_IDS:

        # asking time frame
        timeframe = int(input(f"Enter time ({', '.join([str(i) for i in predict.TIMEFRAMES])} minutes): "))

        if timeframe in predict.TIMEFRAMES:
        # asking input for up down
            up = int(input("Enter 1 for up and 0 for down: "))

            # creating prediction
            result = predict.create(coin=coin, amount=100, timeframe=timeframe, up=up)
            print(f'Result: {result["status"]}')
            print(f'Profit: {result["profit"]}')
        else:
            print("Invalid time.")
    else:
        print("Entered coin is invalid or not supported.")



