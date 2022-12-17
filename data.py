from multiprocessing import reduction
from binance.client import Client
import matplotlib.pyplot as plt
import pandas as pd
import ta
import talib
import numpy as np
import time, sys, os
import requests, math
from datetime import datetime

key_client = 'OIOP5aA2mZVQ9om2ZVdV5MdO7UnxXPM4n5DTL0QmVQMmbhNZxb3g9F4NaaoghnyW'
secret = 'OvsYPIeQfh5Cz4QgzVSKwRZe8HpQOQqjWzZBugmiAqyQxYuIpJSIK6XfKCvhTCYK'

Coins = ["OCEAN", "DAR", "PSG", "REQ", "GHST", "LINK", "TRIBE", "AMP", "RAD"]
MinNotions = [1, 1, 100, 1, 10, 100, 1, 1, 10]
client = Client(key_client, secret)
balanceStart = client.get_asset_balance(asset='BUSD')['free']
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

def Buy(Coin, qty):
    global price, flag
    if flag == False:
        try:
            price = df['Close'][-1]   
            print('Buy - ', price)
            qty = math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)]            
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
    sellpriceprofit = price + (price / 100) * 0.9
    sellpriceloss = price - (price / 100) * 0.9
    Tik = {
        'time' : datetime.now().strftime("%Y-%m-%d %H:%M"),
        'symbol' : symbol,
        'price' : price,
        'sellpriceprofit' : sellpriceprofit,
        'sellpriceloss' : sellpriceloss,
        'qty' : qty,
        'sold' : False,
    }
    x = pd.DataFrame.from_dict(Tik)
    Tikets.append(Tik)
    # print(Tikets)

def Sell(T):
    global Tikets, flag
    quantity = math.floor(T['qty'] * MinNotions[Coins.index(T['symbol'])]) / MinNotions[Coins.index(T['symbol'])]  
    if T['sold'] == False:
        try:
            print('Sell - ', T['sellpriceprofit'], T['sellpriceloss'])
            ReallyBalance = float(client.get_asset_balance(asset=T['symbol'])['free'])
            order = client.create_order(
                    symbol=T['symbol'] + 'BUSD',
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity = quantity 
                    )
            T['sold'] = True
            flag = False
        except Exception as Ext:
            print(Ext)
            ReallyBalance = float(client.get_asset_balance(asset=T['symbol'])['free'])
            print("ERROR OF BALANCE")
            print("BUT WE HAVE - {}".format(ReallyBalance))
            print("AND - ", float(math.floor(ReallyBalance)))
def Maketxt():
    with open('Data.txt', 'a') as f:
        f.writelines("Balance start - {}, Balance end of work - {}".format(BalanceBUSDStart, balances[-1]))
        for T in Tikets:
            f.writelines("{}, \n".format(T))

def CheckTikets(Coin):
    for j in Tikets:
            if j['sold'] == False and j['symbol'] == Coin:
                print("Waiting - ", j['sellpriceprofit'], " ", j['sellpriceloss'], "Now price is - ", df['Close'][-1])
            if j['symbol'] == Coin and j['sold'] == False and (j['sellpriceprofit'] <= price or j['sellpriceloss'] >= price):
                Sell(j)
                CheckBalance()

def CheckBalance():
    global balances
    balanceEnd = client.get_asset_balance(asset='BUSD')['free']
    balances.append(balanceEnd)
    print('Balance in start - {}, Balance in End - {}, percents - {}'.format(BalanceBUSDStart, balanceEnd, float(BalanceBUSDStart) / float(balanceEnd)))

def CheckIndicators(Coin):
    global CounterOfChances
    price = df['Close'][-1]
    if flag == False and df['RSI'][-1] < 35 and df['SMA 30'][-1] > df['SMA 100'][-1]:
        Buy(Coin, math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)])
    if df['RSI'][-1] < 35 and df['SMA 30'][-1] > df['SMA 100'][-1]:
        CounterOfChances += 1

def main():
    global df
    CounterOfChances = 0
    for i in range(31415926535):
        for Coin in Coins:
            df = getminutedata(Coin+'BUSD', '5m', '10000')
            df['RSI'] = ta.momentum.rsi(df.Close, window = 14)
            df['SMA 30'] = talib.SMA(df['Close'].values,timeperiod = 30)
            df['SMA 100'] = talib.SMA(df['Close'].values,timeperiod = 100)
            price = df['Close'][-1]
            CheckTikets(Coin)
            CheckIndicators(Coin)
            
            print(Coin, math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)])
            print('Cycle number - ', i, 'Chances - ', CounterOfChances)
            print(df['RSI'][-1], df['Close'][-1], '\n')
        print('--------------------------')
        time.sleep(60)

try:
    main()
except KeyboardInterrupt:
    print('Interrupted')
    Maketxt()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)