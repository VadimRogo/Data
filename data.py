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
from email.message import EmailMessage
from talib import stream


key_client = 'OIOP5aA2mZVQ9om2ZVdV5MdO7UnxXPM4n5DTL0QmVQMmbhNZxb3g9F4NaaoghnyW'
secret = 'OvsYPIeQfh5Cz4QgzVSKwRZe8HpQOQqjWzZBugmiAqyQxYuIpJSIK6XfKCvhTCYK'
CounterProfitRSI = 1
CounterLossStoch = 1
CounterLossRSI = 1
CounterProfitStoch = 1
Coins = ["OCEAN", "DAR", "AMP", "RAD", "LTC", "QNT", "MIR", "AKRO", "ANC", "TORN", "SLP", "HOOK", "MASK", "DOGE"]
MinNotions = [1, 1, 1, 10, 1000, 1000, 1000, 1000, 1000, 1000, 100, 1, 1, 1]
Qty = [31, 60, 2151, 6.1, 0.118, 0.072, 64.2, 3034, 208.49, 1.96, 3169, 3.8, 3.1, 117]
try:
    client = Client(key_client, secret)
    balanceStart = client.get_asset_balance(asset='BUSD')['free']
except Exception as Ext:
    print(Ext)


Per = [False, False, False, False]
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
        content = str(Ext)

        msg = EmailMessage()
        msg['Subject'] = "Error in Getting data process"
        msg['From'] = sent_from
        msg['To'] = to
        
        msg.set_content(content)
        server.send_message(msg, from_addr=sent_from, to_addrs=to)

def Buy(Coin, qty, type):
    global price
    try:
        price = df['Close'][-1]   
        print('Buy - ', price)        
        order = client.create_order(
                symbol=Coin+'BUSD',
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity = Qty[Coins.index(Coin)]                 
                )
        Tiket(Coin, price, Qty[Coins.index(Coin)], type)
    except Exception as Ext:
        CheckBalance()
        print("Error in buy process, because {}, type of qty {}, qty is {}".format(Ext, type(qty), qty))
        sent_from = gmail_user
        to = ['mrk.main.03@gmail.com']
        msg = EmailMessage()
        msg['Subject'] = "Error in Buy process"
        msg['From'] = sent_from
        msg['To'] = to
        server.send_message(msg, from_addr=sent_from, to_addrs=to)

def Tiket(symbol, price, qty, type):
    global Tikets
    sellpriceprofit = price + (price / 100) * 0.15
    sellpriceloss = price - (price / 100) * 0.15
    Tik = {    
        'time' : datetime.now().strftime("%Y-%m-%d %H:%M"),
        'symbol' : symbol,
        'price' : price,
        'sellpriceprofit' : sellpriceprofit,
        'sellpriceloss' : sellpriceloss,
        'qty' : qty,
        'sold' : False,
        'soldbecause' : "",
        'type' : type
    }

    Tikets.append(Tik)

    if len(Tikets) % 10 == 0:
        sent_from = gmail_user
        to = ['mrk.main.03@gmail.com']
        content = ""
        for T in Tikets:
            content += "{} \n".format(T)
        content += " \n \n \n \n \n "
        msg = EmailMessage()
        msg['Subject'] = "Tikets journal"
        msg['From'] = sent_from
        msg['To'] = to
        msg.set_content(content)
        server.send_message(msg, from_addr=sent_from, to_addrs=to)
    # print(Tikets)

def Sell(T, because):
    global Tikets
    Balance = client.get_asset_balance(asset=T['symbol'])['free']
    quantity = float(math.floor(float(Balance) * MinNotions[Coins.index(T['symbol'])]) / MinNotions[Coins.index(T['symbol'])])
    Coin = T['symbol']
    if T['sold'] == False:
        try:
            print('Sell - ', T['sellpriceprofit'], T['sellpriceloss'])
            ReallyBalance = float(client.get_asset_balance(asset=T['symbol'])['free'])
            order = client.create_order(
                    symbol=T['symbol'] + 'BUSD',
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity =  Qty[Coin.index(Coin)]
                    )
            T['sold'] = True
            T['soldbecause'] = because
            Maketxt(T)
            CheckPermission('Sell')
        except Exception as Ext:
            print(Ext)
            ReallyBalance = float(client.get_asset_balance(asset=T['symbol'])['free'])
            try:
                sent_from = gmail_user
                to = ['mrk.main.03@gmail.com']
                content = str(Ext)
                print(quantity, " -- Quantity")
                msg = EmailMessage()
                msg['Subject'] = "Error in Sell process"
                msg['From'] = sent_from
                msg['To'] = to
                
                msg.set_content(content)
                server.send_message(msg, from_addr=sent_from, to_addrs=to)


                print("ERROR OF BALANCE")
                print("BUT WE HAVE - {}".format(ReallyBalance))
                print("AND - ", float(math.floor(ReallyBalance)))
            except Exception as Ext:
                print(Ext)
def Maketxt(T):
    global CounterProfitRSI, CounterLossRSI, CounterProfitStoch, CounterLossStoch, kpdRSI, KpdStoch
    CheckBalance()
    
    for T in Tikets:
        if T['soldbecause'] == 'profit' and T['type'] == 'RSI':
            CounterProfitRSI += 1
        elif T['soldbecause'] == 'loss' and T['type'] == 'RSI':
            CounterLossRSI += 1
        if T['soldbecause'] == 'profit' and T['type'] == 'Stoch':
            CounterProfitStoch += 1
        elif T['soldbecause'] == 'loss' and T['type'] == 'Stoch':
            CounterLossStoch += 1

        KpdRSI = CounterProfitRSI / CounterLossRSI
        KpdStoch = CounterProfitStoch / CounterLossStoch


    with open('Data.txt', 'a') as f:
        f.writelines("Balance start - {}, Balance end of work - {}".format(BalanceBUSDStart, balances[-1]))
        f.writelines('kpd of Rsi - {} kpd of Stoch - {}'.format(KpdRSI, KpdStoch))
        f.writelines("{}, \n".format(T))

def CheckTikets(Coin):
    for j in Tikets:
            if j['sold'] == False and j['symbol'] == Coin:
                print("Waiting - ", j['sellpriceprofit'], " ", j['sellpriceloss'], "Now price is - ", df['Close'][-1])
            if j['symbol'] == Coin and j['sold'] == False and (j['sellpriceprofit'] <= df['Close'][-1] or j['sellpriceloss'] >= df['Close'][-1]):
                if (j['sellpriceprofit'] <= df['Close'][-1]):
                    Sell(j, "profit")
                else:
                    Sell(j, "loss")
                CheckBalance()

def stoch(Coin):
    global CounterOfChances
    try: 
        sma = talib.SMA(df["Close"], timeperiod=14)
        latest = stream.SMA(df["Close"], timeperiod=14)
        assert (sma[-1] - latest) < 0.00001

        fastk, fastd = talib.STOCHRSI(df["Close"], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        f, fd = stream.STOCHRSI(df["Close"], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
                
        if False in Per and fastk[-1] > 80 and fastk[-1] < 90:
            print('Stoch trying to buy')
            Buy(Coin, 10, 'Stoch')
            print('Bouth')
            CheckPermission('Buy')
        if fastk[-1] > 80 and fastk[-1] < 90:
            CounterOfChances += 1

    except Exception as Ext:
        sent_from = gmail_user
        to = ['mrk.main.03@gmail.com']
        content = str(Ext)

        msg = EmailMessage()
        msg['Subject'] = "Error in Stoch process"
        msg['From'] = sent_from
        msg['To'] = to
        
        msg.set_content(content)
        server.send_message(msg, from_addr=sent_from, to_addrs=to)


def CheckBalance():
    global balances
    try:
        balanceEnd = client.get_asset_balance(asset='BUSD')['free']
        balances.append(balanceEnd)
        print('Balance in start - {}, Balance in End - {}, percents - {}'.format(BalanceBUSDStart, balanceEnd, float(BalanceBUSDStart) / float(balanceEnd)))
    except Exception as Ext:
        sent_from = gmail_user
        to = ['mrk.main.03@gmail.com']
        content = str(Ext)

        msg = EmailMessage()
        msg['Subject'] = "Error in Check Balance process"
        msg['From'] = sent_from
        msg['To'] = to
        
        msg.set_content(content)
        server.send_message(msg, from_addr=sent_from, to_addrs=to)

def CheckIndicators(Coin):
    global CounterOfChances
    price = df['Close'][-1]
    stoch(Coin)
    print('SMA 25 = ', math.floor(df['SMA 25'][-1] * 1000) / 1000, 'SMA 75 = ', math.floor(df['SMA 75'][-1] * 1000) / 1000)
    if (False in Per) and df['RSI'][-1] < 35 and df['SMA 25'][-1] > df['SMA 75'][-1]:
        Buy(Coin, math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)], 'RSI')
        CheckPermission('Buy')
    if df['RSI'][-1] < 35 and df['SMA 25'][-1] > df['SMA 75'][-1]:
        CounterOfChances += 1

def ServerMailConnect():
    global gmail_user, server
    gmail_user = 'mrk.sender.03@gmail.com'
    gmail_password = 'wtnipkdbyijsrujz'

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
    except Exception as Ext:
        print('Something went wrong Email')

def CheckPermission(Operation):
    global Per
    if Operation == 'Buy':
        for x in range(4):
            if Per[x] == False:
                Per[x] = True
                break
    elif Operation == 'Sell':
        for x in range(4):
            if Per[x] == True:
                Per[x] = False
                break

def main():
    global df, price, CounterOfChances
    for i in range(31415926535):
        for Coin in Coins:
            try:
                ServerMailConnect()
                df = getminutedata(Coin+'BUSD', '1m', '10000')
                df['RSI'] = ta.momentum.rsi(df.Close, window = 14)
                df['SMA 25'] = talib.SMA(df['Close'].values,timeperiod = 25)
                df['SMA 75'] = talib.SMA(df['Close'].values,timeperiod = 75)
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
                content = str(Ext)

                msg = EmailMessage()
                msg['Subject'] = "Error in main process"
                msg['From'] = sent_from
                msg['To'] = to
                
                msg.set_content(content)
                server.send_message(msg, from_addr=sent_from, to_addrs=to)
        print('--------------------------')
        time.sleep(60)

try:
    main()
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)