#!/usr/bin/env python
# coding: utf-8

# In[6]:
import pytz


import yfinance as yf
import datetime as dt
import datetime as datetime
import time
from nsepy import get_history
import numpy as np
import pandas as pd
import calendar
import pandas_ta as ta
import requests
from bs4 import BeautifulSoup
import streamlit as st
from dateutil.relativedelta import relativedelta
import holidays as h
holidays = h.get_holidays()

st.set_page_config(page_title='Strategies Dashboard', page_icon=':tada:',layout='wide')
st.title('Strategies Dashboard')
st.markdown("# Main Dashboard Page 📈 ")

def datetotimestamp(date):
    time_tuple = date.timetuple() 
    timestamp= round(time.mktime(time_tuple))
    return timestamp

def timestamptodate(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def exp_data(current_month,current_year):
    df=pd.read_csv('month_expiry.csv')
    df['date'] = pd.to_datetime(df['date'], format = '%d/%m/%Y')
    df['month']= df['date'].apply( lambda x : x.month)
    df['year']= df['date'].apply( lambda x : x.year)
    return df[(df['month']==current_month) & (df['year']==current_year)]

def give_last_5(last_day_date):
    minus=0
    for i in range(20):
        if( (last_day_date in holidays) | (last_day_date.weekday()==6)  | (last_day_date.weekday()==7) | (minus!=6)):
            last_day_date=last_day_date-relativedelta(days=1)
            minus=minus+1
    return last_day_date

def give_last_chris(chris_date):
    for i in range(20):
        if( (chris_date in holidays) | (chris_date.weekday()==5)  | (chris_date.weekday()==6)):
            chris_date=chris_date-relativedelta(days=1)
    return chris_date

# In[7]:


df=pd.DataFrame()
df = yf.download('^NSEI',interval = '1d', period='1y')

master=pd.read_csv('Trading Patterns Anomalies 2022_Updated.csv')

df.reset_index(inplace=True)


# In[8]:


#1 Percentage Change
df['%Change'] = df['Adj Close']/df['Close'].shift(1)-1
#2 20 day Low
df['20_DL'] = np.where((df.Close<=df.Close.rolling(20).min()),'20 DL'," ")
#3 Weekday
df['week'] = df['Date'].apply(lambda x: x.weekday())
#3 Month
df['month'] = df['Date'].apply(lambda x: x.month)
#4 Year
df['year'] = df['Date'].apply(lambda x: x.year)
#5 RSI 2
df['RSI2'] = ta.rsi(df['Adj Close'], timeperiod = 2)
#6 3 Day High
df['3DH'] = df['3DH'] = np.where((df.Close >= df.Close.rolling(3).max()),'3DH'," ")
#7 Outside Day
df['Outside_Day'] = np.where(((df['High'] > df['High'].shift(1)) & (df['Low'] < df['Low'].shift(1))),"Outside Day"," ")
#7 RSI 3 on Abs. Change
df['RSI3_Abs_Change'] = ta.rsi((df['Adj Close'] - df['Adj Close'].shift(1)), timeperiod = 3)
#8 200 EMA
df['200_EMA'] = ta.ema(df['Adj Close'], timeperiod = 200)
#9 200 SMA
df['200_SMA'] = ta.sma(df['Adj Close'], timeperiod = 200)
#10 Pivot Points
df['PP'] = (df['High'].shift(1) + df['Low'].shift(1) + df['Close'].shift(1))/3
#11 S1
df['S1'] = (2*df['PP'] - (df['High'].shift(1)))
#12 R1
df['R1'] = (2*df['PP'] - (df['Low'].shift(1)))
#13 R2
df['R2'] = df['PP'] + (df['High'].shift(1) - df['Low'].shift(1))
#14 RSI10
df['RSI10'] = ta.rsi(df['Adj Close'], timeperiod = 10)
#15 5 Day High
df['5DH'] = df['5DH'] = np.where((df.Close >= df.Close.rolling(5).max()),'5DH'," ")
#16 20 SMA
df['20_SMA'] = ta.sma(df['Adj Close'], timeperiod = 20)

curr_month = df['Date'].iloc[-1].month
curr_year = df['Date'].iloc[-1].year

last_day=calendar.monthrange(curr_year, curr_month)[1]
last_day_date=datetime.date(curr_year,curr_month,last_day)

#gives months last 5th day of trading
month_5_day = give_last_5(last_day_date)

chris_date=datetime.date(curr_year,12,25)

trade_before_chris =  give_last_chris(chris_date)

cur_month_nifty=pd.DataFrame(columns = df.columns)

cur_month_nifty = cur_month_nifty.append(df[(df['month']==curr_month) & (df['year']==curr_year)])
cur_month_nifty.reset_index(inplace=True)

last_15_year = datetime.date(2018,12,15)
alert_15_last=give_last_chris(last_15_year)

#gives current month nifty return in %
cur_month_nifty_per=((cur_month_nifty['Close'].iloc[-1]/cur_month_nifty['Close'].iloc[0])-1)*100

cur_exp_data = exp_data(curr_month,curr_year)
nov_exp_data = exp_data(11,curr_year)

jul_exp_data = exp_data(6,curr_year)

df2=pd.DataFrame()
df2 = yf.download('^NSEBANK',interval = '1d', period='1y')
df2.reset_index(inplace=True)

#1 Percentage Change
df2['%Change'] = df2['Adj Close']/df2['Close'].shift(1)-1
#2 10 Day Low
df2['10_DL'] = np.where((df2.Close<=df2.Close.rolling(10).min()),'10 DL'," ")
#3 Weekday
df2['week'] = df2['Date'].apply(lambda x: x.weekday())
#4 20 day High
df2['20_DH'] = np.where((df2.Close>=df2.Close.rolling(20).max()),'20 DH'," ")
#5 5 Day Low
df2['5_DL'] = np.where((df2.Close<=df2.Close.rolling(5).min()),'5 DL'," ")
#6 250 day High
df2['250_DH'] = np.where((df2.Close>=df2.Close.rolling(250).max()),'250 DH'," ")
#6 Daily Log Returns
df2['Log_returns'] = np.log(df2['Adj Close']/df2['Adj Close'].shift(1))
#3 Month
df2['month'] = df2['Date'].apply(lambda x: x.month)
#3 Year
df2['year'] = df2['Date'].apply(lambda x: x.year)

std_log_ret = np.std(df2['Log_returns'].tail(20))*np.sqrt(20)
mean_log_ret = df2['Log_returns'].tail(20).mean()
sig1 = mean_log_ret - std_log_ret
sig2 = mean_log_ret - (2*std_log_ret)

bbdf2 = ta.bbands(close=df2['Adj Close'],length=20)
#BB Upper
df2['bb_upper']=bbdf2['BBU_20_2.0']
#BB Lower
df2['bb_lower']=bbdf2['BBL_20_2.0']


cur_month_bnnifty=pd.DataFrame(columns = df2.columns)

cur_month_bnnifty = cur_month_bnnifty.append(df2[(df2['month']==curr_month) & (df2['year']==curr_year)])
cur_month_bnnifty.reset_index(inplace=True)


#gives current month nifty return in %
cur_month_bnnifty_per=((cur_month_bnnifty['Close'].iloc[-1]/cur_month_bnnifty['Close'].iloc[0])-1)*100

#Annualized Volatility for 250 Days
x_250_HV = np.std(df2['Log_returns'])*np.sqrt(250)

#Annualized Volatility for 20 Days
y_20_HV = np.std(df2['Log_returns'].tail(20))*np.sqrt(250)





# In[9]:


start=datetotimestamp(datetime.datetime.now().date()-relativedelta(days=40)+datetime.timedelta(hours=9.5))
end= datetotimestamp(datetime.datetime.now().date()+datetime.timedelta(hours=9.4))
url='https://priceapi.moneycontrol.com/techCharts/history?symbol=36&resolution=1D&from='+str(start) + '&to=' +str(end)

resp=requests.get(url).json()
data=pd.DataFrame(resp)

date = []
for dt in data['t']:
    date.append({'Date':timestamptodate(dt).date()})
dt= pd.DataFrame(date)

vixnew = pd.concat([dt,data['c']],axis=1)

vixnew.columns = ['Date', 'Close']
vixnew['10_SMA'] = ta.sma(vixnew['Close'], timeperiod = 10)
vixnew['RSI2'] = ta.rsi(vixnew['Close'], timeperiod = 2)

# In[9]:



conditions_met=pd.DataFrame(columns=['conditions_met'])
#conditions_met = conditions_met.append({'conditions_met':3},ignore_index=True)


# In[10]:


def check():
    conditions_met=pd.DataFrame(columns=['conditions_met'])
    #1. Fri-Mon Effect. Fri <= 0
    if((df['%Change'].iloc[-1] <= 0) & (df['week'].iloc[-1] == 4)):
        conditions_met = conditions_met.append({'conditions_met':1},ignore_index=True)

    #2. Fri-Mon Effect. Fri > 0
    if((df['%Change'].iloc[-1] > 0) & (df['week'].iloc[-1] == 4)):
        conditions_met = conditions_met.append({'conditions_met':2},ignore_index=True)

    #3. Fri-Mon Effect. Fri > 1%
    if((df['%Change'].iloc[-1] > 0.01) & (df['week'].iloc[-1] == 4)):
        conditions_met = conditions_met.append({'conditions_met':3},ignore_index=True)

    #4. Counter Trend Tues
    if((df['%Change'].iloc[-1] <= -0.01) & (df['week'].iloc[-1] == 0)):
        conditions_met = conditions_met.append({'conditions_met':4},ignore_index=True)

    #5. Thurs < -1%
    if((df['%Change'].iloc[-1] <= -0.01) & (df['week'].iloc[-1] == 3)):
        conditions_met = conditions_met.append({'conditions_met':5},ignore_index=True)

    #6. 20 Day Low (Fri)
    if((df['20_DL'].iloc[-1] == '20 DL') & (df['week'].iloc[-1] == 4)):
        conditions_met = conditions_met.append({'conditions_met':6},ignore_index=True)

    #7. 20 Day Low (Mon)
    if((df['20_DL'].iloc[-1] == '20 DL') & (df['week'].iloc[-1] == 0)):
        conditions_met = conditions_met.append({'conditions_met':7},ignore_index=True)

    #8. 20 Day Low (Wed) & Thurs > 0
    if((df['20_DL'].iloc[-2] == '20 DL') & (df['week'].iloc[-1] == 3) & (df['%Change'].iloc[-1] > 0)):
        conditions_met = conditions_met.append({'conditions_met':8},ignore_index=True)

    #9. RSI(3) on Daily Abs. Change (Mon) < 30
    if((df['RSI3_Abs_Change'].iloc[-1] < 30) & (df['week'].iloc[-1] == 0)):
        conditions_met = conditions_met.append({'conditions_met':9},ignore_index=True)

    #10. RSI(3) on Daily Abs. Change (Fri)
    if((df['RSI3_Abs_Change'].iloc[-1] < 30) & (df['week'].iloc[-1] == 4)):
        conditions_met = conditions_met.append({'conditions_met':10},ignore_index=True)

    #11. RSI(3) on Daily Abs. Change (Mon) > 70
    if((df['RSI3_Abs_Change'].iloc[-1] > 70) & (df['week'].iloc[-1] == 0)):
        conditions_met = conditions_met.append({'conditions_met':11},ignore_index=True)

    #12. Outside Day Pattern BTST on Wed < 0
    if((df['Outside_Day'].iloc[-1] == 'Outside Day') & (df['week'].iloc[-1] == 2) & (df['%Change'].iloc[-1] <= 0)):
        conditions_met = conditions_met.append({'conditions_met':12},ignore_index=True)

    #13. 2 Period RSI and Close < 200 EMA on Mon
    if((df['Adj Close'].iloc[-1] < df['200_EMA'].iloc[-1]) & (df['week'].iloc[-1] == 0) & (df['RSI2'].iloc[-1] <= 5)):
        conditions_met = conditions_met.append({'conditions_met':13},ignore_index=True)

    #14. 2 Period RSI and Close > 200 EMA on Thurs
    if((df['Adj Close'].iloc[-1] > df['200_EMA'].iloc[-1]) & (df['week'].iloc[-1] == 3) & (df['RSI2'].iloc[-1] <= 5)):
        conditions_met = conditions_met.append({'conditions_met':14},ignore_index=True)

    #15. 3 Days High & RSI2 > 90 on Fri
    if((df['3DH'].iloc[-1] == '3DH') & (df['week'].iloc[-1] == 4) & (df['RSI2'].iloc[-1] > 90)):
        conditions_met = conditions_met.append({'conditions_met':15},ignore_index=True)

    #16. Cum. RSI(2) (3 Days) < 35 & Close > 200 SMA
    if( ((df['RSI2'].iloc[-1]+df['RSI2'].iloc[-2]+df['RSI2'].iloc[-3])<35) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):   
        conditions_met = conditions_met.append({'conditions_met':16},ignore_index=True)

    #17. Cum. RSI(2) (2 Days) < 35 & Close > 200 SMA
    if( ((df['RSI2'].iloc[-1]+df['RSI2'].iloc[-2])<35) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):
        conditions_met = conditions_met.append({'conditions_met':17},ignore_index=True)

    #18 Cum. RSI(2) (2 Days) < 50 & Close > 200 SMA
    if( ((df['RSI2'].iloc[-1]+df['RSI2'].iloc[-2])<50) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):
        conditions_met = conditions_met.append({'conditions_met':18},ignore_index=True)

    #19 Close = 7 Day Low & Close > 200 SMA
    if( ((np.amin(df['Adj Close'][-7:]))==df['Adj Close'].iloc[-1]) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ): 
        conditions_met = conditions_met.append({'conditions_met':19},ignore_index=True)

    #20 Close is up 4 days in a row & Close < 200 SMA
    if( (df['%Change'].iloc[-4] > 0) & (df['%Change'].iloc[-3] > 0) & (df['%Change'].iloc[-2] > 0) & (df['%Change'].iloc[-1] > 0) & (df['Adj Close'].iloc[-1] < df['200_SMA'].iloc[-1])):
        conditions_met = conditions_met.append({'conditions_met':20},ignore_index=True)

    #21 RSI(2) of VIX > 90 & VIX Close > Previous Day VIX & RSI(2) Index < 30 & Close > 200 EMA
    if( (vixnew['RSI2'].iloc[-1]>90) & (vixnew['Close'].iloc[-1] > vixnew['Close'].iloc[-2]) &  (df['RSI2'].iloc[-1]<30)  &   (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):
        conditions_met = conditions_met.append({'conditions_met':21},ignore_index=True)

    #22 VIX > 5% of 10 DMA (VIX) at least 3 Days & Close > 200 SMA
    if( (vixnew['Close'].iloc[-1] > (1.05*vixnew['10_SMA'].iloc[-1])) & (vixnew['Close'].iloc[-1] > (1.05*vixnew['10_SMA'].iloc[-2])) & ((vixnew['Close'].iloc[-1]) > (1.05*vixnew['10_SMA'].iloc[-3]))  &   (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):         
        conditions_met = conditions_met.append({'conditions_met':22},ignore_index=True)

    #23 RSI(2) < 5 & Close > 200 SMA
    if( (df['RSI2'].iloc[-1] < 5) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):
        conditions_met = conditions_met.append({'conditions_met':23},ignore_index=True)

    #24 Friday Pivot Points v1
    if( (df['week'].iloc[-1] == 4) & (df['%Change'].iloc[-2] < 0 ) & (df['%Change'].iloc[-1] < 0 ) & (df['Open'].iloc[-1] > df['Adj Close'].iloc[-2]) & (df['High'].iloc[-1] > df['R1'].iloc[-1])):
        conditions_met = conditions_met.append({'conditions_met':24},ignore_index=True)

    #25 Friday Pivot Points v2
    if((df['Open'].iloc[-1] > df['S1'].iloc[-1]) & (df['Open'].iloc[-1] < df['R1'].iloc[-1]) & (df['High'].iloc[-1] > df['R2'].iloc[-1]) & (df['Low'].iloc[-1] > df['S1'].iloc[-1]) & (df['Adj Close'].iloc[-1] > df['R1'].iloc[-1])):                 
        conditions_met = conditions_met.append({'conditions_met':25},ignore_index=True)

    #26 Monday 20 Day Low Pivot Points
    if((df['week'].iloc[-1] == 0) & (df['High'].iloc[-1] < df['R1'].iloc[-1]) & (df['20_DL'].iloc[-1] == '20 DL') & (df['Adj Close'].iloc[-1] < df['R1'].iloc[-1])):
        conditions_met = conditions_met.append({'conditions_met':26},ignore_index=True)

    #27 Monday Pivot Points v2
    if((df['week'].iloc[-1] == 0) & (df['%Change'].iloc[-1] < 0) & (df['%Change'].iloc[-2] < 0) & (df['Open'].iloc[-1] > df['Adj Close'].iloc[-2]) & (df['High'].iloc[-1] < df['R1'].iloc[-1])):
        conditions_met = conditions_met.append({'conditions_met':27},ignore_index=True)

    #28 Wednesday Pivot Points
    if((df['week'].iloc[-1] == 2) & (df['Open'].iloc[-1] > df['Adj Close'].iloc[-2]) & (df['%Change'].iloc[-1] > 0) & (df['Adj Close'].iloc[-1] > df['R1'].iloc[-1]) & (df['Low'].iloc[-1] > df['S1'].iloc[-1]) & (df['%Change'].iloc[-3] < 0)):    
        conditions_met = conditions_met.append({'conditions_met':28},ignore_index=True)

    #29 Monday Dip Pivot Points
    if((df['week'].iloc[-1] == 0) & (df['Open'].iloc[-1] < df['Adj Close'].iloc[-2]) & (df['%Change'].iloc[-2] < 0) & (df['High'].iloc[-1] < df['R1'].iloc[-1]) & (df['Low'].iloc[-1] < df['S1'].iloc[-1]) & (df['Adj Close'].iloc[-1] > df['S1'].iloc[-1]) & (df['Adj Close'].iloc[-1] < df['R1'].iloc[-1])):    
        conditions_met = conditions_met.append({'conditions_met':29},ignore_index=True)

    #30 RSI(10)<30 & Close > 200 SMA
    if((df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) & (df['RSI10'].iloc[-1] <= 30)):
        conditions_met = conditions_met.append({'conditions_met':30},ignore_index=True)
              
    #31. Bank Nifty = 10 Day Low & Weekday = Wednesday (OPEX-1) (Short PE at Close (20 Delta))
    if((df2['week'].iloc[-1] == 2) & (df2['10_DL'].iloc[-1] == '10 DL')):
        conditions_met = conditions_met.append({'conditions_met':31},ignore_index=True)

    #32. Bank Nifty is up on Monday (Short ATM-500 PE at Close)
    if((df2['week'].iloc[-1] == 0) & (df2['%Change'].iloc[-1] > 0)):
        conditions_met = conditions_met.append({'conditions_met':32},ignore_index=True)

    #33. Bank Nifty = 10 Day Low & Weekday = Wednesday (OPEX-1) (Short ATM PE Delta)
    if((df2['week'].iloc[-1] == 2) & (df2['10_DL'].iloc[-1] == '10 DL')):
        conditions_met = conditions_met.append({'conditions_met':33},ignore_index=True)

    #34. Bank Nifty is down for 2 consecutive days ahead of OPEX (Short Strangle ATM-300 PE & ATM+300 PE)
    if(((df2['week'].iloc[-2] == 0) & (df2['%Change'].iloc[-2] < 0) & (df2['week'].iloc[-1] == 1) & (df2['%Change'].iloc[-1] < 0)) or ((df2['week'].iloc[-2] == 1) & (df2['%Change'].iloc[-2] < 0) & (df2['week'].iloc[-1] == 2) & (df2['%Change'].iloc[-1] < 0)) or ((df2['week'].iloc[-2] == 4) & (df2['%Change'].iloc[-2] < 0) & (df2['week'].iloc[-1] == 0) & (df2['%Change'].iloc[-1] < 0))):        
        conditions_met = conditions_met.append({'conditions_met':34},ignore_index=True)

    #35. Bank Nifty is at the 20 Day High on OPEX-1 (Short ATM PE at Close)
    if((df2['week'].iloc[-1] == 2) & (df2['20_DH'].iloc[-1] == '20 DH')):
        conditions_met = conditions_met.append({'conditions_met':35},ignore_index=True)

    #36. Bank Nifty is down on Monday (Short Strangle -1% PE & +1% CE)
    if((df2['week'].iloc[-1] == 0) & (df2['%Change'].iloc[-1] < 0)):
        conditions_met = conditions_met.append({'conditions_met':36},ignore_index=True)

    #37. Bank Nifty is 5 Day Low on Opex-1 (Short ATM PE)
    if((df2['week'].iloc[-1] == 2) & (df2['5_DL'].iloc[-1] == '5 DL')):
        conditions_met = conditions_met.append({'conditions_met':37},ignore_index=True)

    #38. Bank Nifty is at the 20 Day High on OPEX-1 (Short Strangle at Close)
    if((df2['week'].iloc[-1] == 2) & (df2['20_DH'].iloc[-1] == '20 DH')):
        conditions_met = conditions_met.append({'conditions_met':38},ignore_index=True)

    #39. Bank Nifty is High in 250 Days (Short ATM PE)
    if((df2['250_DH'].iloc[-1] == '250 DH')):
        conditions_met = conditions_met.append({'conditions_met':39},ignore_index=True)
        
    #40. Bank Nifty 20 Days Historical Volatility > 250 Days Historical Volatility (Short ATM + Straddle Price CE at Close)  on Opex-1
    if((df2['week'].iloc[-1] == 2) & (y_20_HV > x_250_HV)):
        conditions_met = conditions_met.append({'conditions_met':40},ignore_index=True)

    #41. Bank Nifty is down on Monday (Short ATM CE)
    if((df2['week'].iloc[-1] == 0) & (df2['%Change'].iloc[-1] < 0)):
        conditions_met = conditions_met.append({'conditions_met':41},ignore_index=True)

    #42. Worst Single Day Loss in 5 Days on Friday (Short ATM CE ar Close)
    if((df2['week'].iloc[-1] == 4) & (df2['%Change'].iloc[-1] <= df2['%Change'].tail(5).min())):
        conditions_met = conditions_met.append({'conditions_met':42},ignore_index=True)

    #43 Bank Nifty Down on Friday (Short ATM CE with 106% Stop Loss on Premium)
    if((df2['week'].iloc[-1] == 4) & (df2['%Change'].iloc[-1] < 0)):
        conditions_met = conditions_met.append({'conditions_met':43},ignore_index=True)
        
    #44 Bank Nifty is up on First Day of the Month (Short ATM PE)
    if( (len(cur_month_bnnifty)==1) & (cur_month_bnnifty['%Change'].iloc[0] > 0)):
        conditions_met = conditions_met.append({'conditions_met':44},ignore_index=True)

    #45 Nifty & VIX is up for 2 days in a row (Short ATM PE)
    if((df['%Change'].iloc[-1] > 0) & (df['%Change'].iloc[-2] > 0) & (vixnew['Close'].iloc[-1] > vixnew['Close'].iloc[-2]) & (vixnew['Close'].iloc[-2] > vixnew['Close'].iloc[-3])):   
        conditions_met = conditions_met.append({'conditions_met':45},ignore_index=True)

    #46 Nifty is up on first day of the month (Short ATM PE at Close)
    if( (len(cur_month_nifty)==1) & (cur_month_nifty['%Change'].iloc[0] > 0)):
        conditions_met = conditions_met.append({'conditions_met':46},ignore_index=True)

    #47 VIX rises more than 2 points on Monday (Short ATM PE at Close)
    if(((vixnew['Close'].iloc[-1] - vixnew['Close'].iloc[-2]) > 2) & (df['week'].iloc[-1] == 0)):   
        conditions_met = conditions_met.append({'conditions_met':47},ignore_index=True)

    #48 Nifty is 5 Day High on Opex-1 (Short ATM PE at Close)
    if(((df['5DH'].iloc[-1] == '5DH') & (df['week'].iloc[-1] == 2))):   
        conditions_met = conditions_met.append({'conditions_met':48},ignore_index=True)

    #49 Nifty is up on first day of the month (Short ATM PE at Close)
    if( (len(cur_month_nifty)==1) & (cur_month_nifty['%Change'].iloc[0] > 0.01)):
        conditions_met = conditions_met.append({'conditions_met':49},ignore_index=True)
      
    #50 Long Weekend either on Friday or Monday
    if ((df2['Date'].iloc[-1].date() + relativedelta(days=1)) in holidays)  or  ((df2['Date'].iloc[-1].date() + relativedelta(days=3)) in holidays) :
        conditions_met = conditions_met.append({'conditions_met':50},ignore_index=True)
    
    #51 Length of the Monthly Expiry is > 35 Calendar Days
    if( (df['Date'].iloc[-1].date()==cur_exp_data['date'].iloc[0].date()) & ( cur_exp_data['days_to_next_expiry'].iloc[-1]>=35) ):
        conditions_met = conditions_met.append({'conditions_met':51},ignore_index=True)
       
    #52 N is up more than 5% for the month
    if(cur_month_nifty_per>=5 and (df['Date'].iloc[-1].date()==month_5_day)):
        conditions_met = conditions_met.append({'conditions_met':52},ignore_index=True)

    #53 Day before Christmas Anomaly
    if(df['Date'].iloc[-1].date()==trade_before_chris):
        conditions_met = conditions_met.append({'conditions_met':53},ignore_index=True)
        
    #54 New Year from 15th December
    if(df['Date'].iloc[-1].date()==alert_15_last):
        conditions_met = conditions_met.append({'conditions_met':54},ignore_index=True)
        
    #55 November-December Expiry
    if(df['Date'].iloc[-1].date()==nov_exp_data['date'].iloc[0].date()):
        conditions_met = conditions_met.append({'conditions_met':55},ignore_index=True)
    
    #56 July Anomaly
    if(df['Date'].iloc[-1].date()==jul_exp_data['date'].iloc[0].date()):
        conditions_met = conditions_met.append({'conditions_met':56},ignore_index=True)
        
    #57 BN Closes below Lower Bollinger Band
    if( (df2['Adj Close'].iloc[-1] < df2['bb_lower'].iloc[-1] ) ):
        conditions_met = conditions_met.append({'conditions_met':57},ignore_index=True)
        
    #58 BN is down for 3 or more days on Tuesday
    if( (df2['week'].iloc[-2] == 2) & (df2['%Change'].iloc[-3] < 0) & (df2['%Change'].iloc[-2] < 0) & (df2['%Change'].iloc[-1] < 0)):        
        conditions_met = conditions_met.append({'conditions_met':58},ignore_index=True)
        
    #59 N Current Day Low > Previous Day Close (Gap-Up)
    if(df['Low'].iloc[-1] > df['Adj Close'].iloc[-2]):
        conditions_met = conditions_met.append({'conditions_met':59},ignore_index=True)
        
    #60 N Closes above 20 DMA on current day & Closed below 20 DMA on previous day
    if( (df['Adj Close'].iloc[-1] > df['20_SMA'].iloc[-1] ) & (df['Adj Close'].iloc[-2] < df['20_SMA'].iloc[-2]) ):
        conditions_met = conditions_met.append({'conditions_met':60},ignore_index=True)
        
    #61 BN is down by more than 1 Std. Dev & HV(20) > HV(250)
    if((y_20_HV > x_250_HV) &  (df2['Log_returns'].iloc[-1]< sig1)):
        conditions_met = conditions_met.append({'conditions_met':61},ignore_index=True)

    #62 BN is down by more than 2 Std. Dev
    if((df2['Log_returns'].iloc[-1]< sig2)):
        conditions_met = conditions_met.append({'conditions_met':62},ignore_index=True)

    #63 Current day is Friday & today's Range < 70% of Avg. Range in last 3 days or > 140% of Avg. Range in 3 last days & today's  %Change > 0
    if( ((df['%Change'].iloc[-1] > 0 ) & (df['week'].iloc[-1] == 4)  & ((df['High'].iloc[-1] - df['Low'].iloc[-1]) > (1.4* ((df['High'] - df['Low'])[-4:-1].mean()) )))  or ( ( df['%Change'].iloc[-1] > 0 ) & (df['week'].iloc[-1] == 4)  &  ((df['High'].iloc[-1] - df['Low'].iloc[-1]) < (0.7*((df['High'] - df['Low'])[-4:-1].mean() ) )) )  ) :
        conditions_met = conditions_met.append({'conditions_met':63},ignore_index=True)
        
    #64 N Today's High is > Previous 2 days High & High 2 days ago is < Low 5 Days ago & Close > Open
    if( (df['Adj Close'].iloc[-1] > df['Open'].iloc[-1] ) & (df['High'].iloc[-1] >df['High'].iloc[-2]) & (df['High'].iloc[-1] >df['High'].iloc[-3]) & (df['High'].iloc[-3] < df['Low'].iloc[-6]) ):
        conditions_met = conditions_met.append({'conditions_met':64},ignore_index=True)
    

    conditions_met=conditions_met.sort_values('conditions_met')

    display=pd.DataFrame(columns = master.columns)

    for index,row in conditions_met.iterrows():
        display = display.append(master[master['Condition']==row['conditions_met']])
    
 
    if(len(display)==0):
        st.header('No Conditions met today')
    if(len(display)!=0):
        st.dataframe(display)

user_input = st.empty()

user_input1 = user_input.text_input("Enter Password", '')

if(user_input1=='kartik'):
    st.button('Get current conditions', on_click=check())
    st.header('Nifty Data')
    st.dataframe(df[-10:])
    st.header('BankNifty Data')
    st.dataframe(df2[-10:])
    st.header('Vix Data')
    st.dataframe(vixnew[-5:])
    if user_input1 != "":
        user_input.empty()

st.text('Made with ❤️ by Kartik')


