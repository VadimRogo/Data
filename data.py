from multiprocessing import reduction
from binance.client import Client
import matplotlib.pyplot as plt
import pandas as pd
import ta
import talib
import numpy as np
import time, sys, os
import requests, math
import smtplib
from datetime import datetime

key_client = 'OIOP5aA2mZVQ9om2ZVdV5MdO7UnxXPM4n5DTL0QmVQMmbhNZxb3g9F4NaaoghnyW'
secret = 'OvsYPIeQfh5Cz4QgzVSKwRZe8HpQOQqjWzZBugmiAqyQxYuIpJSIK6XfKCvhTCYK'

Coins = ["OCEAN", "DAR", "PSG", "REQ", "LINK", "TRIBE", "AMP", "RAD", "BNX", "BTC", "LTC", "ETH", "QNT"]
MinNotions = [1, 1, 100, 1, 100, 1, 1, 10, 1000, 100000, 1000, 10000, 1000]
try:
    client = Client(key_client, secret)
    balanceStart = client.get_asset_balance(asset='BUSD')['free']
except Exception as Ext:
    print(Ext)

flag = False

Tikets = []

CounterOfChances = 0
BalanceBUSDStart = client.get_asset_balance(asset='BUSD')['free']
balances = []
def getminutedata(symbol, interval, lookback):
    try:
        frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                        interval,
                                                        lookback + 'min ago UTC'))
        frame = frame.iloc[:,:6]
        frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        frame = frame.set_index('Time')
        frame.index = pd.to_datetime(frame.index, unit='ms')
        frame = frame.astype(float)
        return frame
    except Exception as Ext:
        sent_from = gmail_user
        to = ['mrk.main.03@gmail.com']
        email_text = "Subject : {} \n \n {}".format("Error in getting data", Ext)
        server.sendmail(sent_from, to, email_text)
        print(Ext)

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
            sent_from = gmail_user
            to = ['mrk.main.03@gmail.com']
            email_text = "Subject : {} \n \n {}".format("Error in Buy process", Ext)
            server.sendmail(sent_from, to, email_text)
            print(Ext)


def Tiket(symbol, price, qty):
    global Tikets
    sellpriceprofit = price + (price / 100) * 0.25
    sellpriceloss = price - (price / 100) * 0.4
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
    if len(Tikets) > 10:
        sent_from = gmail_user
        to = ['mrk.main.03@gmail.com']
        email_text = "Subject : Journal of Tikets \n \n "
        for Tik in Tikets:
            email_text += "{} \n".format(Tik)
        email_text += "Num of chances - {}".format(CounterOfChances)
        server.sendmail(sent_from, to, email_text)
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
            Maketxt(T)
            flag = False
        except Exception as Ext:
            print(Ext)
            ReallyBalance = float(client.get_asset_balance(asset=T['symbol'])['free'])
            sent_from = gmail_user
            to = ['mrk.main.03@gmail.com']
            email_text = "Subject : {} \n \n {}".format("Error in Sell process", Ext)
            server.sendmail(sent_from, to, email_text)
            print("ERROR OF BALANCE")
            print("BUT WE HAVE - {}".format(ReallyBalance))
            print("AND - ", float(math.floor(ReallyBalance)))
def Maketxt(T):
    with open('Data.txt', 'a') as f:
        f.writelines("Balance start - {}, Balance end of work - {}".format(BalanceBUSDStart, balances[-1]))
        f.writelines("{}, \n".format(T))

def CheckTikets(Coin):
    for j in Tikets:
            if j['sold'] == False and j['symbol'] == Coin:
                print("Waiting - ", j['sellpriceprofit'], " ", j['sellpriceloss'], "Now price is - ", df['Close'][-1])
            if j['symbol'] == Coin and j['sold'] == False and (j['sellpriceprofit'] <= df['Close'][-1] or j['sellpriceloss'] >= df['Close'][-1]):
                Sell(j)
                CheckBalance()

def CheckBalance():
    global balances
    try:
        balanceEnd = client.get_asset_balance(asset='BUSD')['free']
        balances.append(balanceEnd)
        print('Balance in start - {}, Balance in End - {}, percents - {}'.format(BalanceBUSDStart, balanceEnd, float(BalanceBUSDStart) / float(balanceEnd)))
    except Exception as Ext:
        sent_from = gmail_user
        to = ['mrk.main.03@gmail.com']
        email_text = "Subject : {} \n \n {}".format("Error in CheckBalance", Ext)
        server.sendmail(sent_from, to, email_text)
        print(Ext)

def CheckIndicators(Coin):
    global CounterOfChances
    price = df['Close'][-1]
    print('SMA 30 = ', math.floor(df['SMA 30'][-1] * 1000) / 1000, 'SMA 100 = ', math.floor(df['SMA 100'][-1] * 1000) / 1000)
    if flag == False and df['RSI'][-1] < 35 and df['SMA 30'][-1] > df['SMA 100'][-1]:
        Buy(Coin, math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)])
    if df['RSI'][-1] < 35 and df['SMA 30'][-1] > df['SMA 100'][-1]:
        print('All fine')
        CounterOfChances += 1

def ServerMailConnect():
    global gmail_user, server
    gmail_user = 'mrk.sender.03@gmail.com'
    gmail_password = 'fgdyccspculyfkrp'

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
    except Exception as Ext:
        print('Something went wrong Email')



def main():
    global df, price
    ServerMailConnect()
    CounterOfChances = 0
    for i in range(31415926535):
        for Coin in Coins:
            try:
                df = getminutedata(Coin+'BUSD', '5m', '10000')
                df['RSI'] = ta.momentum.rsi(df.Close, window = 14)
                df['SMA 30'] = talib.SMA(df['Close'].values,timeperiod = 30)
                df['SMA 100'] = talib.SMA(df['Close'].values,timeperiod = 100)
                price = df['Close'][-1]

                CheckIndicators(Coin)
                CheckTikets(Coin)

                print(Coin, math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)])
                print('Cycle number - ', i, 'Chances - ', CounterOfChances)
                print(df['RSI'][-1], df['Close'][-1], '\n')
            except Exception as Ext:
                print(Ext)
                sent_from = gmail_user
                to = ['mrk.main.03@gmail.com']
                email_text = "Subject : {} \n \n {}".format("Error in main def", Ext)
                server.sendmail(sent_from, to, email_text)
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