# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 12:30:34 2021
@author: angus
"""
import pandas as pd
import datetime
import requests
import csv

# Read excel
df_main = pd.read_excel('SFC.xlsx',sheet_name = 'Sheet1')

# gather most recent date
date = pd.to_datetime(df_main['Date'], dayfirst = True)
date = date.max()

d = datetime.timedelta(days=7) ## add a week
date = date + d

date1 = date.strftime('%Y%m%d')
date = date.strftime('%Y/%m/%d')

# gather data using date
header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

url = ('https://www.sfc.hk/-/media/EN/pdf/spr/' + date + '/Short_Position_Reporting_Aggregated_Data_' + date1 + '.csv')

r = requests.get(url, headers=header)
    # save as CSV
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
for ticker in yf_ticker: ## equiv excel formula: IF(LEN(B2)>4,CONCAT(REPT("0",5-LEN(B2)),B2,".HK"),CONCAT(REPT("0",4-LEN(B2)),B2,".HK"))
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

### vlookup data from yahoo finance. If data does not exist, we need to update the yf data sheet
df_yf = pd.read_excel('SFC.xlsx',sheet_name = 'yf data')
df_yf = df_yf[['Yf Ticker', 'Sector', 'Industry']]
df_new = df_new.merge(df_yf, on = ['Yf Ticker'], how = 'left')

### vlookup data from HKEX. If data doesn't exist... 
df_hkex = pd.read_excel('SFC.xlsx',sheet_name = 'HKEX')
df_hkex ['Stock Code'] = df_hkex ['Stock Code'].astype(str)
df_hkex = df_hkex[['Stock Code','Shares Outstanding', 'Market Cap (Dec 21)']]
df_new = df_new.merge(df_hkex, on = ['Stock Code'], how = 'left')

### vlookup data from the hkex excels 
## Add Chinese Name
df_hkexcn = pd.read_excel('SFC.xlsx',sheet_name = 'HKEX listed_CN', header = 2)
df_hkexcn = df_hkexcn [['股份代號','股份名稱']]
df_hkexcn = df_hkexcn.rename({'股份代號': 'Stock Code', '股份名稱': 'Stock Name CN'}, axis='columns')
df_hkexcn ['Stock Code'] = df_hkexcn ['Stock Code'].astype(str)
df_new = df_new.merge(df_hkexcn, on = ['Stock Code'], how = 'left')

## Add if it is listed column. Equiv excel formula: IFNA(IF(VLOOKUP(B2,'HKEX listed_CN'!$A:$B,1,0)=B2,1,0),0)
df_listed = df_new [['Stock Code']]
df_hkexcn = df_hkexcn ['Stock Code']

df_hkexcn = df_hkexcn.values.tolist()
df_listed = df_listed.isin(df_hkexcn)
df_listed = df_listed.astype(int)
df_listed = df_listed.rename({'Stock Code': 'Listed?'}, axis='columns')

df_new = pd.concat([df_new, df_listed], axis =1)

## add if it is an etf column
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
