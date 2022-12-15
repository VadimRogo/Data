from multiprocessing import reduction
from binance.client import Client
import matplotlib.pyplot as plt
import pandas as pd
import ta
import numpy as np
import time, sys, os
import requests, math
from datetime import datetime

key_client = 'OIOP5aA2mZVQ9om2ZVdV5MdO7UnxXPM4n5DTL0QmVQMmbhNZxb3g9F4NaaoghnyW'
secret = 'OvsYPIeQfh5Cz4QgzVSKwRZe8HpQOQqjWzZBugmiAqyQxYuIpJSIK6XfKCvhTCYK'

Coins = ["OCEAN", "DAR", "ACA", "DGB", "MOB"]
CoinsQty = [120, 125, 156, 2550, 16.9]

client = Client(key_client, secret)

flag = False

Tikets = []

CounterOfChances = 0
BalanceBUSDStart = client.get_asset_balance(asset='BUSD')['free']
balances = []
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


def getBalanceBUSD():
    Balance = client.get_asset_balance(asset='BUSD')['free']
    return Balance

def Buy(Coin, qty):
    global price, flag
    if flag == False:
        try:
            
            price = df['Close'][-1]   
            print('Buy - ', price)
            qty = CoinsQty[Coins.index(Coin)]                 
            order = client.create_order(
                    symbol=Coin+'BUSD',
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity = qty                 
                    )
            flag = True
            Tiket(Coin, price, qty)
        except Exception as Ext:
            print(Ext)


def Tiket(symbol, price, qty):
    global Tikets
    sellpriceprofit = price + price * (0.5 / 100)
    sellpriceloss = price - price * (0.8 / 100)
    Tik = {
        'time' : datetime.now().strftime("%Y-%m-%d %H:%M"),
        'symbol' : symbol,
        'price' : price,
        'sellpriceprofit' : sellpriceprofit,
        'sellpriceloss' : sellpriceloss,
        'qty' : qty,
        'sold' : False,
    }
    Tikets.append(Tik)
    print(Tikets)

def Sell(T):
    global Tikets, flag
    if T['sold'] == False:
        try:
            print('Sell - ', T['sellpriceprofit'])
            balance = CoinsQty[Coins.index(T['symbol'])]
            ReallyBalance = float(client.get_asset_balance(asset=T['symbol'])['free'])
            order = client.create_order(
                    symbol=T['symbol'] + 'BUSD',
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity = math.floor(ReallyBalance * 10) 
                    )
            T['sold'] = True
            flag = False
        except Exception as Ext:
            print(Ext)
            balance = CoinsQty[Coins.index(T['symbol'])]
            ReallyBalance = float(client.get_asset_balance(asset=T['symbol'])['free'])
            print("ERROR OF BALANCE")
            print("BALANCE EQUAL - {}, BUT WE HAVE - {}".format(balance, ReallyBalance))
def Maketxt():
    with open('Data.txt', 'a') as f:
        f.writelines(str(Tikets))

def main():
    global df
    balanceStart = getBalanceBUSD()
    CounterOfChances = 0
    for i in range(31415926535):
        for Coin in Coins:
            df = getminutedata(Coin+'BUSD', '1m', '100')
            df['RSI'] = ta.momentum.rsi(df.Close, window = 14)
            price = df['Close'][-1]


            for j in Tikets:
                if j['sold'] == False and j['symbol'] == Coin:
                    print("Waiting - ", j['sellpriceprofit'], " ", j['sellpriceloss'], "Now price is - ", df['Close'][-1])
                if j['symbol'] == Coin and j['sold'] == False and (j['sellpriceprofit'] <= price or j['sellpriceloss'] >= price):
                    Sell(j)
                    balanceEnd = getBalanceBUSD()
                    balances.append(balanceEnd)
                    print('Balance in start - {}, Balance in End - {}, percents - {}'.format(balanceStart, balanceEnd, float(balanceStart) / float(balanceEnd)))
            
            if flag == False and df['RSI'][-1] < 35:
                Buy(Coin, CoinsQty[Coins.index(Coin)])
            if df['RSI'][-1] < 35:
                CounterOfChances += 1
            
            print(Coin, CoinsQty[Coins.index(Coin)])
            print('Cycle number - ', i)
            print('Chances - ', CounterOfChances)
            print(df['RSI'][-1], '\n')
        print('--------------------------')
        time.sleep(15)


try:
    main()
except KeyboardInterrupt:
    print('Interrupted')
    Maketxt()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)