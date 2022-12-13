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




def MakingPlots():
    plt.plot(range(0, len(df['Close'])), df['Close'])
    plt.show()

    plt.plot(range(0, len(df['RSI'])), df['RSI'])
    plt.show()


def Buy():
    global price, flag
    if flag == False:
        try:
            print('Buy - ', price)
            price = df['Close'][-1]
            qty = 153       
            order = client.create_order(
                    symbol='OCEANBUSD',
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity = 153
                    )
            Tiket(price, qty)
            flag = True
        except Exception as Ext:
            print(Ext)

def Tiket(price, qty):
    global Tikets
    sellpriceprofit = price + price / 100
    sellpriceloss = price - price / 100
    Tik = {
        'price' : price,
        'sellpriceprofit' : sellpriceprofit,
        'sellpriceloss' : sellpriceloss,
        'qty' : qty,
        'sold' : False,
    }
    Tikets.append(Tik)
    print(Tikets)

def Sell(T):
    global Tikets
    if T['sold'] == False:
        try:
            print('Sell - ', T['sellpriceprofit'])
            order = client.create_order(
                    symbol='OCEANBUSD',
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity = 152
                    )
            T['sold'] = True
            flag = False
        except Exception as Ext:
            print(Ext)

for i in range(100000000):
    df = getminutedata('OCEANBUSD', '1m', '100')
    df['RSI'] = ta.momentum.rsi(df.Close, window = 14)
    price = df['Close'][-1]
    for j in Tikets:
        if j['sold'] == False and (j['sellpriceprofit'] > price or j['sellpriceloss']):
            Sell(j)
    if flag == False and df['RSI'][-1] < 35:
        Buy()
    print('Cycle number - ', i, df['Close'][-1])
    print(df['RSI'][-1])
    time.sleep(60)



print(df)

