# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 12:30:34 2021

@author: angus
"""

import pandas as pd
import yfinance as yf
import pandas as pd
import requests
import csv
import multitasking
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


############ Code for scraping SFC website for their short positions data
# dates = pd.read_excel('SFC Dates.xlsx')


# dates = dates.values.tolist()
# header = {
#   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
#   "X-Requested-With": "XMLHttpRequest"
# }

# sfc = []

# for date in dates :
#     date [0]
#     url = ('https://www.sfc.hk/-/media/EN/pdf/spr/' + date [0] + '/Short_Position_Reporting_Aggregated_Data_' + str(date[1]) + '.csv')
    
#     r = requests.get(url, headers=header)
#     a = r.text
#     lines = a.splitlines()
#     reader = csv.reader(lines)
#     parsed_csv = list(reader)

#     sfc.extend(parsed_csv)
# df = pd.DataFrame(sfc)
# df.to_excel("sfc.xlsx")  
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

# # tickers = pd.read_excel('SFC.xlsx')
# # tickers2 = tickers.groupby('Stock Code').count()
# # tickers2 = tickers2.index

# tickers2 = ["405", "435", "778", "808", "823", "1426", "1503", "1881", "2778", "87001"]


# # tickers2 = [1, 2,3,4,5, 9.88888]

# shr_out8 = [['Stock Code', 'Shares Outstanding', 'Shares Outstanding As Of']]

# @multitasking.task # <== this is all it takes :-)
# def shr_out_threaded (stock, shr_out8):
#     try: 
#         driver = webdriver.Chrome(options=chrome_options) ### use google chrome
#         url = 'https://www.hkex.com.hk/Market-Data/Securities-Prices/Real-Estate-Investment-Trusts/Real-Estate-Investment-Trusts-Quote?sym=' + str(stock) +'&sc_lang=en'
#         driver.get(url) ### go to website
#         sleep(1) ### gives time for page to load. This is a xueqiu specific solution
#         html = driver.page_source ## gather and read HTML       
        
#         soup = BeautifulSoup(html, 'html.parser')
#         shr_out = soup.find(class_= "ico_data col_issued_shares")
#         shr_out = shr_out.get_text()
#         shr_out = shr_out.split(' (as at ')
        
#         shr_out8.append([str(stock),shr_out[0],shr_out[1]])
        
#         driver.quit()
#     except AttributeError:
#         shr_out = ['NA', 'NA']
#         shr_out8.append([str(stock),shr_out[0],shr_out[1]])
#         driver.quit()
#     except IndexError:
#         shr_out = soup.find_all(class_= "ico_data col_issued_shares")
        
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
# df.to_excel("shares_outstanding.xlsx")  



# msft = yf.Ticker('1917.HK')
# abc = msft.info

######################Adding market cap and business summary data from yahoo finance
# tickers = pd.read_excel('SFC.xlsx')
# tickers2 = tickers.groupby('Yf Ticker').count()
# tickers2 = tickers2.index

tickers2 = ["0013.HK", "2015.HK", "2162.HK", "2190.HK", "2219.HK"]


@multitasking.task # <== this is all it takes :-)
def info_threaded(ticker, yfinance):
    try: 
        msft = yf.Ticker(ticker)
        abc = msft.info
        abcd = abc ['marketCap']
        abcde = abc ['longBusinessSummary']
        asdfdas = [ticker, abcd, abcde]
        yfinance.append(asdfdas)
    except KeyError:
        asdfdas = [ticker, 'NA', 'NA']
        yfinance.append(asdfdas)

# tickers = ['6628.HK', 'MSFT', 'APPL']
yfinance = []
for ticker in tickers2:
    info_threaded(ticker, yfinance)
while len(yfinance) < len(tickers2):
    sleep(0.01)

df = pd.DataFrame(yfinance)
# df.to_excel("mkt_cap.xlsx")  

# print(yfinance)







