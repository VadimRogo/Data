from binance.client import Client
import matplotlib.pyplot as plt
import pandas as pd
import ta
import talib
import numpy as np
import time, sys, os
import requests, math
import smtplib
from Keys import SECRET, KEY, KEYMAIL
from datetime import datetime
from email.message import EmailMessage
from talib import stream


key_client = KEY
secret = SECRET
key_mail = KEYMAIL
CounterProfitRSI = 1
CounterLossStoch = 1
CounterLossRSI = 1
CounterProfitEMA10 = 1
CounterLossEMA10 = 1
CounterProfitEMA25 = 1
CounterLossEMA25 = 1
CounterProfitStoch = 1
CounterOfErrors = 0
CounterJournal = 0
kpdRSI = 0
RealCounterOfChances = 0
Coins = ["BTC", "DAR", "ETH", "DOGE", "DASH", "LINK"]
MinNotions = [100000, 1, 10000, 1, 1000, 100]

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
        MaketxtError('GetData', Ext)
        SendMail('Getting Data', Ext)
        print(Ext)


def SendMail(Where, Ext):
    sent_from = "mrk.sender.02@gmail.com"
    to = ['mrk.main.03@gmail.com']
    content = str(Ext)

    msg = EmailMessage()
    msg['Subject'] = "Error in {}".format(Where)
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
                quantity = qty         
                )
        Tiket(Coin, price, qty, type)
    except Exception as Ext:
        print(Ext)
        SendMail('Buy Process', Ext)
        MaketxtError('Buy', Ext)

def Tiket(symbol, price, qty, type):
    global Tikets, CounterJournal
    sellpriceprofit = price + (price / 100) * 0.5
    sellpriceloss = price - (price / 100) * 0.5
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
        sent_from = "mrk.sender.02@gmail.com"
        to = ['mrk.main.03@gmail.com']
        content = ''
        CounterJournal += 1
        for i in Tikets:
            content += i + '\n'

        msg = EmailMessage()
        msg['Subject'] = "Tikets journal {}",format(CounterJournal)
        msg['From'] = sent_from
        msg['To'] = to
        
        msg.set_content(content)
        server.send_message(msg, from_addr=sent_from, to_addrs=to)
    # print(Tikets)

def Sell(T, because):
    global Tikets
    Balance = client.get_asset_balance(asset=T['symbol'])['free']
    quantity = float(math.floor(float(Balance) * float(MinNotions[Coins.index(T['symbol'])])) / float(MinNotions[Coins.index(T['symbol'])]))
    Coin = T['symbol']
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
            CheckPermission('Sell')
            if float(Balance) > 30 / float(T['price']):
                CheckPermission('Sell')
                CheckPermission('Sell')
                for j in Tikets:
                    if j['symbol'] == T['symbol']:
                        j['sold'] = True 
            if float(Balance) > 20 / float(T['price']):
                CheckPermission('Sell')
                for j in Tikets:
                    if j['symbol'] == T['symbol']:
                        j['sold'] = True 
                
            

            T['sold'] = True
            # T['soldbecause'] = because
            Maketxt(str(T))
            
        except Exception as Ext:
            print(Ext)
            MaketxtError('Sell', Ext)
            print('Quantity we tried to sell - ', quantity, 'Min notional - ', MinNotions[Coins.index(T['symbol'])])
            SendMail('Sell process Coin1 - {} \n Error - '.format(T['symbol'], Ext), Ext)
            ReallyBalance = float(client.get_asset_balance(asset=T['symbol'])['free'])
            
def Maketxt(T):
    global CounterProfitRSI, CounterLossRSI, CounterProfitStoch, CounterLossStoch, kpdRSI, KpdStoch, CounterProfitEMA10, CounterLossEMA10, CounterProfitEMA25, CounterLossEMA25
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
        if T['soldbecause'] == 'profit' and T['type'] == 'EMA 10':
            CounterProfitEMA10 += 1
        elif T['soldbecause'] == 'loss' and T['type'] == 'EMA 10':
            CounterLossEMA10 += 1
        if T['soldbecause'] == 'profit' and T['type'] == 'EMA 25':
            CounterProfitEMA25 += 1
        elif T['soldbecause'] == 'loss' and T['type'] == 'EMA 25':
            CounterLossEMA25 += 1


        KpdRSI = CounterProfitRSI / CounterLossRSI
        KpdStoch = CounterProfitStoch / CounterLossStoch
        KpdEMA10 = CounterProfitEMA10 / CounterLossEMA10
        KpdEMA25 = CounterProfitEMA25 / CounterLossEMA25 

    with open('Data.txt', 'w') as f:
        f.writelines("Balance start - {}, Balance end of work - {}  ".format(BalanceBUSDStart, balances[-1]))
        f.writelines("Efficency of work {}  ".format(BalanceBUSDStart / balances[-1]))
        f.writelines("Was {} deals RSI and {} deals Stoch and {} deals EMA10 and {} deals EMA25".format(CounterLossRSI + CounterProfitRSI, CounterProfitStoch + CounterLossStoch, CounterLossEMA10 + CounterProfitEMA10, CounterLossEMA25 + CounterProfitEMA25))
        f.writelines("Efficency of Rsi - {} Efficency of Stoch - {} Efficency of EMA10 - {} Efficency of EMA25 - {}".format(KpdRSI, KpdStoch, KpdEMA10, KpdEMA25))
        f.writelines("EMA10 profit counter - {}, EMA10 loss counter - {}, EMA25 profit counter - {}, EMA25 loss counter - {}".format(CounterProfitEMA10, CounterLossEMA10, CounterProfitEMA25, CounterLossEMA25))
        f.writelines("Rsi profit counter - {}, Rsi loss counter - {}, Stoch profit counter - {}, Stoch loss counter - {}".format(CounterProfitRSI, CounterLossRSI, CounterProfitStoch, CounterLossStoch))

def MaketxtError(Where, Ext):
    global CounterOfErrors 
    CounterOfErrors += 1    
    with open('Errors.txt', 'a') as f:
        f.writelines("Error in {}, {}".format(Where, Ext))

        

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
    global CounterOfChances, RealCounterOfChances
    try: 
        sma = talib.SMA(df["Close"], timeperiod=14)
        latest = stream.SMA(df["Close"], timeperiod=14)
        assert (sma[-1] - latest) < 0.00001

        fastk, fastd = talib.STOCHRSI(df["Close"], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        f, fd = stream.STOCHRSI(df["Close"], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
                
        if False in Per and float(fastk[-1]) > 10 and float(fastk[-1]) < 20:
            print('Stoch trying to buy')
            Buy(Coin, float(math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)]), 'Stoch')
            CheckPermission('Buy')
            RealCounterOfChances +=1
            CounterOfChances += 1
        if float(fastk[-1]) > 10 and float(fastk[-1]) < 20:
            CounterOfChances += 1

    except Exception as Ext:
        MaketxtError('Stoch', Ext)
        SendMail('Stoch indicator', Ext)
        print(Ext)

def CheckBalance():
    global balances
    try:
        balanceEnd = client.get_asset_balance(asset='BUSD')['free']
        balances.append(balanceEnd)
        print('Balance in start - {}, Balance in End - {}, percents - {}'.format(BalanceBUSDStart, balanceEnd, float(BalanceBUSDStart) / float(balanceEnd)))
    except Exception as Ext:
        print(Ext)
        SendMail('Check balance process', Ext)
        MaketxtError('Balance', Ext)

def CheckIndicators(Coin):
    global CounterOfChances, RealCounterOfChances
    price = df['Close'][-1]
    stoch(Coin)
    print('SMA 25 = ', math.floor(df['SMA 25'][-1] * 1000) / 1000, 'SMA 75 = ', math.floor(df['SMA 75'][-1] * 1000) / 1000)
    if (False in Per) and df['RSI'][-1] < 35 and df['SMA 25'][-1] < df['SMA 75'][-1] and df['SMA 25'][-10] < df['SMA 75'][-10]:
        Buy(Coin, math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)], 'RSI')
        CheckPermission('Buy')
        RealCounterOfChances += 1
        CounterOfChances += 1

    if (False in Per) and df['RSI5'][-1] < 35 and df['SMA 25'][-14] < df['SMA 75'][-14]:
        Buy(Coin, math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)], 'RSI')
        CheckPermission('Buy')
        RealCounterOfChances += 1
        CounterOfChances += 1

    if False in Per and df['EMA 25'][-1] + df['EMA 25'][-1] / 1000 > price and  df['EMA 25'][-1] - df['EMA 25'][-1] / 1000 < price and df['EMA 25'][-5] > df['Close'][-5]:
        Buy(Coin, math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)], 'EMA 25')
        CheckPermission('Buy')
        RealCounterOfChances += 1
        CounterOfChances += 1

    if df['RSI'][-1] < 35 and df['SMA 25'][-1] > df['SMA 75'][-1]:
        CounterOfChances += 1
    if df['EMA 25'][-1] + df['EMA 25'][-1] / 1000 > price and  df['EMA 25'][-1] - df['EMA 25'][-1] / 1000 < price and df['EMA 25'][-5] > df['Close'][-5]:
        CounterOfChances += 1
    if df['RSI5'][-1] < 35 :
        CounterOfChances += 1

def CheckPermission(Operation):
    global Per
    if Operation == 'Buy':
        for x in range(3):
            if Per[x] == False:
                Per[x] = True
                break
    elif Operation == 'Sell':
        for x in range(3):
            if Per[x] == True:
                Per[x] = False
                break
def ServerMailConnect():
    global gmail_user, server
    gmail_user = 'mrk.sender.02@gmail.com'
    gmail_password = key_mail

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
    except Exception as Ext:
        print('Something went wrong Email')
            

def main():
    global df, price, CounterOfChances
    for i in range(31415926535):
        for Coin in Coins:
            try:
                df = getminutedata(Coin+'BUSD', '5m', '10000')
                df5 = getminutedata(Coin+'BUSD', '5m', '10000')
                df['RSI5'] = ta.momentum.rsi(df5.Close, window = 14) 
                df['RSI'] = ta.momentum.rsi(df.Close, window = 14)
                df['SMA 25'] = talib.SMA(df['Close'].values,timeperiod = 25)
                df['SMA 75'] = talib.SMA(df['Close'].values,timeperiod = 75)
                df['EMA 10'] = talib.EMA(df['Close'], 10)
                df['EMA 25'] = talib.EMA(df['Close'], 25)
                price = df['Close'][-1]
                
                ServerMailConnect()
                CheckIndicators(Coin)
                
                CheckTikets(Coin)

                print(Coin, math.floor(11 / price * MinNotions[Coins.index(Coin)]) / MinNotions[Coins.index(Coin)])
                print('Cycle number - ', i, 'Chances - ', CounterOfChances, 'Real Chances - ', RealCounterOfChances)
                print(df['RSI'][-1], df['Close'][-1], '\n')
            except Exception as Ext:
                print(Ext)
                SendMail('Main process', Ext)
                MaketxtError('Main', Ext)
        print('--------------------------')
        time.sleep(60)

try:
    ServerMailConnect()
    main()
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
