# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 16:18:56 2021
@author: angus
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import investpy
import yfinance as yf
import datetime as dt

st.set_page_config(layout="wide")
st.title('HKEX Short Positions')

@st.cache(ttl= 1800) ## Data would need to get reloaded every 30 minutes
def load_data(link):
    df = pd.read_excel(link,sheet_name='Sheet1', header = 0, engine = 'openpyxl', parse_dates = False)
    df = df.loc[df['Listed?'] == 1] ### Filters rows where it is still listed
    df = df.loc[df['ETF?'] == 0] ### Filters rows where it is not an ETF
    df = df.loc[df['Stock Name'].str[-2:] != '-T'] ### Filters out stocks which are trading only under the NASDAQ-AMEX pilot program
    df['Date']= pd.to_datetime(df['Date'], dayfirst = True)### converts Date column to datetime variable
    return df
link = r'SFC.xlsx'
df = load_data(link)

st.write('**Key Assumptions: **')
st.write('**Total shares used as denominator for Share Shorted % uses data from the HKEX website on Dec 21.**')
st.write('**For dual class shares, shares outstanding only refers to the component listed**')
st.write('**We only examine companies that are still listed on HKEX as of Dec 21**')
st.write ('All assumptions and further info can be found in [documentation](https://github.com/epiphronquant/HKEX_shortsell)')
### mkt cap sliding filter
slider = st.slider("Select Market Cap in HKD 100's of million", min_value=0, value=(0,50000) ,max_value=50000)
slider = tuple([100000000*x for x in slider])
df = df[df['Market Cap (Dec 21)'].between(slider [0], slider [1])]

column_1, column_2 = st.columns(2) ### Divides page into 2 columns
with column_1:## dropdown box for share measurement
    share_measurement = ["Share Shorted %", "Aggregated Reportable Short Positions (HK$)"]
    share_measurement = st.selectbox(
        'Which measure of shares shorted should we use?',
          share_measurement)
    'You selected: ', share_measurement
        
with column_2: ### Dropdown box for median or mean
    central_tendancy = ['Average', 'Median']
    select_central = st.selectbox(
        'Average or Median?',
          central_tendancy)
    'You selected: ', select_central
### dropdown box for sector
sectors = ["Healthcare", "All", "Industrials", "Utilities", "Real Estate", "Financial Services", "Communication Services", "Consumer Cyclical", "Technology", "Consumer Defensive", "Basic Materials", "Energy"]
sector = st.selectbox(
    'Which sector are you interested in?',
      sectors)
'You selected: ', sector
 
### create barchart given data
def bar_chart(x, y1, y2, title, tickformat = ''):
    fig = go.Figure(
            data=[go.Bar(name='Count', x=x, y=y1, yaxis='y', offsetgroup=1),
                go.Bar(name=share_measurement, x=x, y=y2, yaxis='y2', offsetgroup=2)],
            layout={'yaxis': {'title': 'Count'},
                'yaxis2': {'title': share_measurement, 'overlaying': 'y', 'side': 'right', 'tickformat': tickformat}})
    fig.update_layout(barmode='group',title={'text': title})
    fig.update_xaxes(categoryorder='max descending')
    return fig

column_1, column_2 = st.columns(2) ### Divides page into 2 columns
with column_1:### Sector Chart
    @st.cache(suppress_st_warning=False)
    def chart_1(df, share_measurement, select_central):
        chart1 = df [['Aggregated Reportable Short Positions (HK$)','Share Shorted %','Sector', 'Stock Name', 'Date']]
        date = chart1 ['Date'].max()
        chart1 = chart1.loc[df['Date'] == date]
        a = chart1.groupby(['Stock Name','Sector']).count() ### gathers data by sector
        a = a.groupby (['Sector']).count()
        industries = a.index
        industries = industries.tolist()
        
        a = a[share_measurement]
        a = a.rename('Count')
        a  = a.to_list()
        if select_central == 'Average':
            b = chart1.groupby(['Sector']).mean() ### gathers data by sector
            b = b[share_measurement]        
        else:
            b = chart1.groupby(['Sector']).median() ### gathers data by sector
            b = b[share_measurement]        
        b = b.to_list()
        date = date.strftime('%b %d, %Y')
        fig = bar_chart(industries, a, b,"Sector Companies Count and " + select_central +' ' + share_measurement + ' as of ' + date)
        return fig  
    fig = chart_1(df, share_measurement, select_central)    
    st.plotly_chart(fig)
### filters data by sector
if sector == 'All':
    df = df 
else:
    df = df.loc[df['Sector'] == sector]

with column_2:### Industry Chart
    chart1 = df [['Aggregated Reportable Short Positions (HK$)','Share Shorted %', 'Stock Name', 'Industry', 'Date']]
    date = chart1 ['Date'].max()
    chart1 = chart1.loc[df['Date'] == date]
    a = chart1.groupby(['Stock Name','Industry']).count() ### gathers data by industry
    a = a.groupby (['Industry']).count()
    industries = a.index
    industries = industries.tolist()
    a = a[share_measurement] 
    a = a.rename('Count')
    a  = a.to_list()    
    if select_central == 'Average':
        b = chart1.groupby(['Industry']).mean() ### gathers data by industry
        b = b[share_measurement]    
    else:
        b = chart1.groupby(['Industry']).median() ### gathers data by industry
        b = b[share_measurement]
    
    b = b.to_list()
    date = date.strftime('%b %d, %Y')

    fig = bar_chart(industries, a, b,sector +' Sub Sector' +" Companies Count and " + select_central +' ' + share_measurement + ' as of ' + date)
    st.plotly_chart(fig)
### Sector performance with short measurement chart
performance = df [['Date', share_measurement]]
if select_central == 'Average':
    a = performance.groupby(['Date']).mean()

else:
    a = performance.groupby(['Date']).median()

fig = make_subplots(specs=[[{"secondary_y": True}]])
    #add a box to select HSI or HSH as second axis
index = st.selectbox(
    'Which index would you like to compare it to?',
      ['Hang Seng Healthcare Index', 'Hang Seng Index'])
'You selected: ', index
    # Download HSH and HSI data
start = a.index[0].strftime('%d/%m/%Y')
# end = a.index[-1].strftime('%d/%m/%Y')
end = dt.date.today()
end = end.strftime('%d/%m/%Y')

if index == 'Hang Seng Index':
    df_index = investpy.get_index_historical_data(index='Hang Seng',
                                        country='hong kong',
                                        from_date= start,
                                        to_date= end)
else:
    df_index = investpy.get_index_historical_data(index='hs healthcare',
                                            country='hong kong',
                                            from_date= start,
                                            to_date= end)
    # Add traces
fig.add_trace(go.Scatter(x= a.index, y= a[share_measurement], name= select_central + ' '+ share_measurement),
    secondary_y=False)

fig.add_trace(go.Scatter(x = df_index.index, y= df_index['Close'], name= index),
    secondary_y=True)
    # Add figure title
fig.update_layout(title_text= sector + ' '+share_measurement + ' and ' + index + ' Chart')
    # Set x-axis title
fig.update_xaxes(title_text="Date")
    # Set y-axes titles
fig.update_yaxes(title_text= sector+ ' ' + select_central + ' '+ share_measurement, secondary_y=False)
fig.update_yaxes(title_text= index + ' '+ "Level", secondary_y=True)
st.plotly_chart(fig, use_container_width=True)

######### make line chart on industry
industry = industries
industry = st.selectbox(
    'Which industry are you interested in?',
      industries)
'You selected: ', industry

###### Download HSH and HSI data
performance = df.loc[df['Industry'] == industry]
performance = performance [['Date', 'Industry', 'Stock Name', share_measurement]]

if select_central == 'Average':
    a = performance.groupby(['Date']).mean()

else:
    a = performance.groupby(['Date']).median()
    
start = a.index[0].strftime('%d/%m/%Y')
# end = a.index[-1].strftime('%d/%m/%Y')
end = dt.date.today()
end = end.strftime('%d/%m/%Y')
if index == 'Hang Seng Index':
    df_index = investpy.get_index_historical_data(index='Hang Seng',
                                        country='hong kong',
                                        from_date= start,
                                        to_date= end)
else:
    df_index = investpy.get_index_historical_data(index='hs healthcare',
                                            country='hong kong',
                                            from_date= start,
                                            to_date= end)
fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
fig.add_trace(go.Scatter(x= a.index, y= a[share_measurement], name= select_central + ' '+ share_measurement),
    secondary_y=False)

fig.add_trace(go.Scatter(x = df_index.index, y= df_index['Close'], name= index),
    secondary_y=True)
    # Add figure title
fig.update_layout(title_text= industry + ' '+ share_measurement + ' and ' + index + ' Chart')
    # Set x-axis title
fig.update_xaxes(title_text="Date")
    # Set y-axes titles
fig.update_yaxes(title_text= industry + ' '+ select_central + ' '+ share_measurement, secondary_y=False)
fig.update_yaxes(title_text="Index Level", secondary_y=True)
st.plotly_chart(fig, use_container_width=True)

## add a column displaying stock with the highest monthly increase in shortsell
date = df ['Date'].max()
df1 = df.loc[df['Date'] == date]
d = dt.timedelta(days=28) ## selects one month. This must be done in multiples of 7 given the SFC dataset
date2 = date - d
df2 = df.loc[df['Date'] == date2]
df_2 = df1 [['Stock Code', 'Share Shorted %']]
df2 = df2.rename(columns = {'Share Shorted %':'Share Shorted % -1 month'})

df_2 = df_2 [['Stock Code', 'Share Shorted %']]

df2 = df2.merge(df_2, on='Stock Code', how='left')
df2 ['Last Month Share Short Pct Pt Change'] = df2 ['Share Shorted %'] - df2 ['Share Shorted % -1 month']
df2 = df2 [['Last Month Share Short Pct Pt Change','Stock Code']]

df1 = df1.merge(df2, on='Stock Code', how='left')

date = date.strftime('%b %d, %Y')
### chart displaying key information of raw data
@st.cache()
def chart_5(df1, select_central, sector):
    if select_central == 'Average':
        df1 = df1.groupby(['Stock Name']).mean()
    
    else:
        df1 = df1.groupby(['Stock Name']).median()
    df1 = df1.drop(columns = ['ETF?', 'Listed?'])
    df1 = df1.drop(['Aggregated Reportable Short Positions (Shares)', 'Shares Outstanding'], axis =1)
    dict1 = df [['Stock Name', 'Stock Name CN','Industry']]
    
    dict1 = dict1.drop_duplicates(subset=None, keep='first', inplace=False)
    
    df1 = df1.merge(dict1, on='Stock Name', how='left')
    column_name = ["Stock Name", "Stock Name CN", "Stock Code", "Aggregated Reportable Short Positions (HK$)", "Share Shorted %", 'Last Month Share Short Pct Pt Change', "Market Cap (Dec 21)", "Industry"]
    df1 = df1.reindex(columns=column_name)
    df1 ['Stock Code'] = df1['Stock Code'].astype(int)
    df1 = df1.sort_values(by=['Share Shorted %'], ascending = False)
    return df1
st.write('')
st.write ('Chart below only shows short data from ' + date)
df1 = chart_5(df1, select_central, sector)
df1

########## line chart on company
performance = df [['Date', 'Stock Name', 'Yf Ticker', 'Stock Code', share_measurement]]
companies = performance['Stock Name']
companies = companies.tolist()
companies = list(dict.fromkeys(companies))
tickers = performance['Stock Code']
tickers = tickers.tolist()
tickers = list(dict.fromkeys(tickers))
companies.extend(tickers)
company = st.selectbox( ### can select tickers and company name for individual company chart
    'Which company/stock code are you interested in?',
      companies)
'You selected: ', company

if type(company) == int: ## if input is a ticker
    company = performance.loc[performance['Stock Code'] == company, 'Stock Name'] 
    company = company.iloc[0]
else:
    pass    
@st.cache(suppress_st_warning=False, allow_output_mutation=True)
def chart_6 (performance, company, share_measurement, sector):
    performance = performance.loc[performance['Stock Name'] == company]
    a = performance    
    a.sort_values(by='Date', inplace=True)
    a = a.set_index ('Date')
    start = a.index[0].strftime('%Y-%m-%d')
    #end = a.index[-1]
    #end = end + pd.DateOffset(1)
    #end = end.strftime('%Y-%m-%d')
    ticker = a ['Yf Ticker']
    ticker = ticker[0]
    
    df_index = yf.download(ticker, start= start)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add traces
    fig.add_trace(go.Scatter(x= a.index, y= a[share_measurement], name= select_central + ' '+ share_measurement),
        secondary_y=False)
    
    fig.add_trace(go.Scatter(x = df_index.index, y= df_index['Adj Close'], name= company),
        secondary_y=True)
    # Add figure title
    fig.update_layout(title_text= company + ' ' + share_measurement + ' and ' + company + ' Stock Chart')
    # Set x-axis title
    fig.update_xaxes(title_text="Date")
    # Set y-axes titles
    fig.update_yaxes(title_text= company + ' '+ share_measurement, secondary_y=False)
    fig.update_yaxes(title_text= company + " Adjusted Closing Price (HKD)", secondary_y=True)
    return fig
fig = chart_6(performance, company, share_measurement, sector)
st.plotly_chart(fig, use_container_width=True)

## Link to github where you can download the file
st.write("[Download the full data file](https://github.com/epiphronquant/HKEX_shortsell/raw/main/SFC.xlsx)")
