# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 12:30:34 2021

@author: angus
"""

import pandas as pd
import datetime
# import yfinance as yf
# import pandas as pd
import requests
import csv
# import multitasking
# from time import sleep
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options


############ Code for scraping SFC website for their short positions data

# Read excel
df_main = pd.read_excel('SFC.xlsx',sheet_name = 'Sheet1')

# gather most recent date
date = pd.to_datetime(df_main['Date'], dayfirst = True)
date = date.max()

d = datetime.timedelta(days=7)
date = date + d

date1 = date.strftime('%Y%m%d')
date = date.strftime('%Y/%m/%d')

# gather data
header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

url = ('https://www.sfc.hk/-/media/EN/pdf/spr/' + date + '/Short_Position_Reporting_Aggregated_Data_' + date1 + '.csv')

r = requests.get(url, headers=header)
a = r.text
lines = a.splitlines()
reader = csv.reader(lines)
parsed_csv = list(reader)

df_new = pd.DataFrame(parsed_csv)
new_header = df_new.iloc[0] #grab the first row for the header
df_new = df_new[1:] #take the data less the header row
df_new.columns = new_header #set the header row as the df header

### add yf ticker, sector etc to gathered data
yf_ticker = df_new ['Stock Code']

yf_ticker1 = []
for ticker in yf_ticker: ## =IF(LEN(B2)>4,CONCAT(REPT("0",5-LEN(B2)),B2,".HK"),CONCAT(REPT("0",4-LEN(B2)),B2,".HK"))
    if len(ticker) >4:                
        abc =  (5 - len(ticker)) *"0"
        abc = abc + ticker + ".HK"
        abc = [ticker, abc]
        yf_ticker1.append(abc)
    else:
        abc =  (4 - len(ticker)) *"0"
        abc = abc + ticker + ".HK"
        abc = [ticker, abc]
        yf_ticker1.append(abc)

yf_ticker = pd.DataFrame(yf_ticker1, columns = ['Stock Code','Yf Ticker'])

df_new = df_new.merge(yf_ticker, on = ['Stock Code'], how = 'left')

### vlookup data from yahoo finance
df_yf = pd.read_excel('SFC.xlsx',sheet_name = 'yf data')
df_yf = df_yf[['Yf Ticker', 'Sector', 'Industry']]
df_new = df_new.merge(df_yf, on = ['Yf Ticker'], how = 'left')

### vlookup data from HKEX
## 'HKEX'
df_hkex = pd.read_excel('SFC.xlsx',sheet_name = 'HKEX')
df_hkex ['Stock Code'] = df_hkex ['Stock Code'].astype(str)
df_hkex = df_hkex[['Stock Code','Shares Outstanding', 'Market Cap (Dec 21)']]
df_new = df_new.merge(df_hkex, on = ['Stock Code'], how = 'left')

### vlookup data from the hkex excels 
## 'HKEX etf", "HKEX listed", "HKEX listed_CN"
## Add Chinese Name
df_hkexcn = pd.read_excel('SFC.xlsx',sheet_name = 'HKEX listed_CN', header = 2)
df_hkexcn = df_hkexcn [['股份代號','股份名稱']]
df_hkexcn = df_hkexcn.rename({'股份代號': 'Stock Code', '股份名稱': 'Stock Name CN'}, axis='columns')
df_hkexcn ['Stock Code'] = df_hkexcn ['Stock Code'].astype(str)
df_new = df_new.merge(df_hkexcn, on = ['Stock Code'], how = 'left')

## Add if it is listed
##=IFNA(IF(VLOOKUP(B2,'HKEX listed_CN'!$A:$B,1,0)=B2,1,0),0)
df_listed = df_new [['Stock Code']]
df_hkexcn = df_hkexcn ['Stock Code']

df_hkexcn = df_hkexcn.values.tolist()
df_listed = df_listed.isin(df_hkexcn)
df_listed = df_listed.astype(int)
df_listed = df_listed.rename({'Stock Code': 'Listed?'}, axis='columns')

df_new = pd.concat([df_new, df_listed], axis =1)

## add if it is an etf
df_etf = pd.read_excel('SFC.xlsx',sheet_name = 'HKEX etf', header = 1)
df_etf = df_etf ['Stock code*']
df_etf = df_etf.dropna()
df_etf = df_etf.astype(int)
df_etf = df_etf.astype(str)

df_etf = df_etf.values.tolist()

df_etf0 = df_new [['Stock Code']]
df_etf0 = df_etf0.isin(df_etf)
df_etf0 = df_etf0.astype(int)
df_etf0 = df_etf0.rename({'Stock Code': 'ETF?'}, axis='columns')
df_new = pd.concat([df_new, df_etf0], axis =1)

### add Share Shorted % column
sharepct = df_new [['Shares Outstanding', 'Aggregated Reportable Short Positions (Shares)']]
sharepct ['Aggregated Reportable Short Positions (Shares)'] = sharepct ['Aggregated Reportable Short Positions (Shares)'].astype(float)

sharepct ['Share Shorted %'] = sharepct ['Aggregated Reportable Short Positions (Shares)']  / sharepct ['Shares Outstanding'] * 100

df_new = pd.concat([df_new, sharepct ['Share Shorted %']], axis =1)

df_new[["Stock Code", "Aggregated Reportable Short Positions (Shares)", "Aggregated Reportable Short Positions (HK$)"]] = df_new[["Stock Code", "Aggregated Reportable Short Positions (Shares)", "Aggregated Reportable Short Positions (HK$)"]].apply(pd.to_numeric)
### concat gathered data with main data

df_main = pd.concat ([df_main, df_new])

### write updated main data to excel
with pd.ExcelWriter('SFC.xlsx',
                     mode='a', engine = 'openpyxl', if_sheet_exists = 'replace') as writer:  
     df_main.to_excel(writer, sheet_name='Sheet1', index = False)


#################### Code for adding Yahoo Finance Sector and Industry data
# tickers = pd.read_excel('SFC.xlsx')
# tickers2 = tickers.groupby('Yf Ticker').count()
# tickers2 = tickers2.index

# @multitasking.task # <== this is all it takes :-)
# def info_threaded(ticker, yfinance):
#     try: 
#         msft = yf.Ticker(ticker)
#         abc = msft.info
#         abcd = abc ['sector']
#         abcde = abc ['industry']
#         asdfdas = [ticker, abcd, abcde]
#         yfinance.append(asdfdas)
#     except KeyError:
#         asdfdas = [ticker, 'NA', 'NA']
#         yfinance.append(asdfdas)

# # tickers = ['6628.HK', 'MSFT', 'APPL']
# yfinance = []
# for ticker in tickers2:
#     info_threaded(ticker, yfinance)
# while len(yfinance) < len(tickers2):
#     sleep(0.01)

# df = pd.DataFrame(yfinance)
# df.to_excel("sectors.xlsx")  

# print(yfinance)

# ####################### scraping HKEX data on shares outstanding
# # tickers = pd.read_excel('SFC.xlsx')
# # tickers2 = tickers.groupby('Stock Code').count()
# # tickers2 = tickers2.index
# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')

# # tickers = pd.read_excel('SFC.xlsx')
# # tickers2 = tickers.groupby('Stock Code').count()
# # tickers2 = tickers2.index

# tickers2 = ["1024","1810","2015","2057","3690","6608","9618","9626","9698","9868","9888","9959","9991"]


# # tickers2 = [1, 2,3,4,5, 9.88888]

# shr_out8 = [['Stock Code', 'Shares Outstanding', 'Shares Outstanding As Of']]

# @multitasking.task # <== this is all it takes :-)
# def shr_out_threaded (stock, shr_out8):
#     try: 
#         driver = webdriver.Chrome(options=chrome_options) ### use google chrome
#         url = 'https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=' + str(stock) +'&sc_lang=en'
#         driver.get(url) ### go to website
#         sleep(1) ### gives time for page to load. This is a xueqiu specific solution
#         html = driver.page_source ## gather and read HTML       
        
#         soup = BeautifulSoup(html, 'html.parser')
#         shr_out = soup.find(class_= "col_issued_shares")
#         shr_out = shr_out.get_text()
#         shr_out = shr_out.split(' (as at ')
        
#         shr_out8.append([str(stock),shr_out[0],shr_out[1]])
        
#         driver.quit()
#     except AttributeError:
#         shr_out = ['NA', 'NA']
#         shr_out8.append([str(stock),shr_out[0],shr_out[1]])
#         driver.quit()
#     except IndexError:
#         shr_out = soup.find_all(class_= "col_issued_shares")
        
#         shr_out = str(shr_out)
#         shr_out = shr_out.split('<br/>')
#         for shares in shr_out:
#             if '(Listed' in shares:
#                 shr_out = shares
#         shr_out = shr_out.split(' (Listed ')
#         shr_out8.append([str(stock),shr_out[0],shr_out[1]])
        
#         driver.quit()
# for stock in tickers2:
#     shr_out_threaded(stock, shr_out8)
# while len(shr_out8)-1 < len(tickers2):
#     sleep(0.01)

# df = pd.DataFrame(shr_out8)
# # df.to_excel("shares_outstanding.xlsx")  

############### some values don't show up on REITs, this must be manually added with the code below from other HKEX url
# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
# multipliers = {'K':1000, 'M':1000000, 'B':1000000000}

# def string_to_float(string):
#     if string[-1].isdigit(): # check if no suffix
#         return int(string)
#     mult = multipliers[string[-1]] # look up suffix to get multiplier
#      # convert number to float, multiply by multiplier, then make int
#     return float(string[:-1]) * mult
# # # tickers = pd.read_excel('SFC.xlsx')
# # # tickers2 = tickers.groupby('Stock Code').count()
# # # tickers2 = tickers2.index

# tickers2 = ["808","7345"]


# # # tickers2 = [1, 2,3,4,5, 9.88888]

# shr_out8 = [['Stock Code', 'Shares Outstanding', 'Shares Outstanding As Of', 'Mkt Cap']]

# @multitasking.task # <== this is all it takes :-)
# def shr_out_threaded (stock, shr_out8):
#     try: 
#         driver = webdriver.Chrome(options=chrome_options) ### use google chrome
#         url = 'https://www.hkex.com.hk/Market-Data/Securities-Prices/Real-Estate-Investment-Trusts/Real-Estate-Investment-Trusts-Quote?sym=' + str(stock) +'&sc_lang=en'
#         driver.get(url) ### go to website
#         sleep(1) ### gives time for page to load. This is a xueqiu specific solution
#         html = driver.page_source ## gather and read HTML       
#         driver.quit()

#         soup = BeautifulSoup(html, 'html.parser')
#         shr_out = soup.find(class_= "ico_data col_issued_shares")
#         shr_out = shr_out.get_text()
#         shr_out = shr_out.split(' (as at ')      
        
#     except AttributeError:
#         shr_out = ['NA', 'NA']
    
#     try:
#         shr_out[1]
#     except IndexError:
#         shr_out = soup.find_all(class_= "ico_data col_issued_shares")
        
#         shr_out = str(shr_out)
#         shr_out = shr_out.split('<br/>')
#         for shares in shr_out:
#             if '(Listed' in shares:
#                 shr_out = shares
#         shr_out = shr_out.split(' (Listed ')
        
#     mktcap = soup.find(class_= "ico_data col_mktcap") ### mkt cap needs to be fixed for the data scraper
#     try:
#         mktcap = mktcap.get_text()
#         mktcap = mktcap.replace('HK$','')
#         mktcap = mktcap.replace('HKD','')
#         mktcap = mktcap.replace('RMB','')
#         mktcap = mktcap.replace(',','')
#         mktcap = string_to_float(mktcap)

#     except AttributeError:
#         mktcap = 'NA'
#     shr_out8.append([str(stock),shr_out[0],shr_out[1], mktcap])
# for stock in tickers2:
#     shr_out_threaded(stock, shr_out8)
# while len(shr_out8)-1 < len(tickers2):
#     sleep(0.01)

# df = pd.DataFrame(shr_out8)
# df.to_excel("shares_outstanding.xlsx")  



# msft = yf.Ticker('1917.HK')
# abc = msft.info

######################Adding market cap and business summary data from yahoo finance
# tickers = pd.read_excel('SFC.xlsx')
# tickers2 = tickers.groupby('Yf Ticker').count()
# tickers2 = tickers2.index

# tickers2 = ["0013.HK", "2015.HK", "2162.HK", "2190.HK", "2219.HK"]


# @multitasking.task # <== this is all it takes :-)
# def info_threaded(ticker, yfinance):
#     try: 
#         msft = yf.Ticker(ticker)
#         abc = msft.info
#         abcd = abc ['marketCap']
#         abcde = abc ['longBusinessSummary']
#         asdfdas = [ticker, abcd, abcde]
#         yfinance.append(asdfdas)
#     except KeyError:
#         asdfdas = [ticker, 'NA', 'NA']
#         yfinance.append(asdfdas)

# # tickers = ['6628.HK', 'MSFT', 'APPL']
# yfinance = []
# for ticker in tickers2:
#     info_threaded(ticker, yfinance)
# while len(yfinance) < len(tickers2):
#     sleep(0.01)

# df = pd.DataFrame(yfinance)
# df.to_excel("mkt_cap.xlsx")  

# print(yfinance)







