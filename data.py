from multiprocessing import reduction
from binance.client import Client
import matplotlib.pyplot as plt
import pandas as pd
import ta
import numpy as np
import time
import requests

key_client = 'OIOP5aA2mZVQ9om2ZVdV5MdO7UnxXPM4n5DTL0QmVQMmbhNZxb3g9F4NaaoghnyW'
secret = 'OvsYPIeQfh5Cz4QgzVSKwRZe8HpQOQqjWzZBugmiAqyQxYuIpJSIK6XfKCvhTCYK'

Coins = ["OCEANBUSD", "DARBUSD"]
CoinsQty = [133, 26.1]


client = Client(key_client, secret)

flag = False

Tikets = []

def getminutedata(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                    interval,
                                                    lookback + 'min ago UTC'))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

def Buy(Coin, qty):
    global price, flag
    if flag == False:
        try:
            print('Buy - ', price)
            price = df['Close'][-1]
            qty = CoinsQty[Coins.index(Coin)]
            order = client.create_order(
                    symbol=Coin,
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity = qty      
                    )
            flag = True
            Tiket(Coin, price, qty)
        except Exception as Ext:
            print(Ext)

def Sell(T):
    global Tikets
    if T['sold'] == False:
        try:
            print('Sell - ', T['sellpriceprofit'])
            order = client.create_order(
                    symbol='OCEANBUSD',
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity = T['qty']
                    )
            T['sold'] = True
            flag = False
        except Exception as Ext:
            print(Ext)



def Tiket(symbol, price, qty):
    global Tikets
    sellpriceprofit = price
    sellpriceloss = price 
    Tik = {
        'symbol' : symbol,
        'price' : price,
        'sellpriceprofit' : sellpriceprofit,
        'sellpriceloss' : sellpriceloss,
        'qty' : round(qty - qty * 5/100, 1),
        'sold' : False,
    }
    Tikets.append(Tik)
    print(Tikets)


for i in range(100000000):
    for Coin in Coins:
        df = getminutedata(Coin, '1m', '100')
        df['RSI'] = ta.momentum.rsi(df.Close, window = 14)
        price = df['Close'][-1]
  
        print(Coin, CoinsQty[Coins.index(Coin)])
        print('Cycle number - ', i, df['Close'][-1])
        print(df['RSI'][-1])
   
    time.sleep(15)



print(df)

