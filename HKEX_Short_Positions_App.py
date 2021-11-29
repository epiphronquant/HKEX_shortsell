# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 16:18:56 2021

@author: angus
"""
import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import investpy
import yfinance as yf
import base64
from io import BytesIO

st.set_page_config(layout="wide")
st.title('HKEX Short Positions')

@st.cache
def load_data(link):
    df = pd.read_excel(link,sheet_name='Sheet1', header = 0, engine = 'openpyxl', parse_dates = False)
    # df_export = df
    df = df.loc[df['Listed?'] == 1] ### Filters rows where it is still listed
    df = df.loc[df['ETF?'] == 0] ### Filters rows where it is not an ETF
    df = df.loc[df['Stock Name'].str[-2:] != '-T'] ### Filters out stocks which are trading only under the NASDAQ-AMEX pilot program
    df['Date']= pd.to_datetime(df['Date'], dayfirst = True)### converts date to datetime variable
    return df
link = r'SFC.xlsx'
df = load_data(link)

slider = st.slider("Select Market Cap in 100's of millions", min_value=0, value=(0,5000) ,max_value=5000)
slider = tuple([100000000*x for x in slider])

# if slider 
df = df[df['Market Cap (Nov 24)'].between(slider [0], slider [1])]

column_1, column_2 = st.columns(2) ### Divides page into 2 columns
with column_1:### Chart of distribution and Lead 1 Chart
    sectors = ["Healthcare", "All", "Industrials", "Utilities", "Real Estate", "Financial Services", "Communication Services", "Consumer Cyclical", "Technology", "Consumer Defensive", "Basic Materials", "Energy"]
    sector = st.selectbox(
        'Which sector are you interested in?',
          sectors)
    'You selected: ', sector
    
with column_2:
    ### Dropdown box for median or mean
    central_tendancy = ['Average', 'Median']
    select_central = st.selectbox(
        'Average or Median?',
          central_tendancy)
    'You selected: ', select_central
   
share_measurement = ["Share Shorted %", "Aggregated Reportable Short Positions (HK$)"]
share_measurement = st.selectbox(
    'Which measure of shares shorted should we use?',
      share_measurement)
'You selected: ', share_measurement
 
if share_measurement == "Aggregated Reportable Short Positions (HK$)":
    tickformat = ''
else:
    tickformat = ''
def bar_chart(x, y1, y2, title, tickformat = ',.0%'):
    fig = go.Figure(
            data=[go.Bar(name='Count', x=x, y=y1, yaxis='y', offsetgroup=1),
                go.Bar(name=share_measurement, x=x, y=y2, yaxis='y2', offsetgroup=2)],
            layout={'yaxis': {'title': 'Count'},
                'yaxis2': {'title': share_measurement, 'overlaying': 'y', 'side': 'right', 'tickformat': tickformat}})
    fig.update_layout(barmode='group',title={'text': title})
    fig.update_xaxes(categoryorder='max descending')
    return fig

### bar charts must filter by most recent
column_1, column_2 = st.columns(2) ### Divides page into 2 columns
with column_1:### Chart of distribution and Lead 1 Chart
    chart1 = df [['Aggregated Reportable Short Positions (HK$)','Share Shorted %','Sector', 'Stock Name', 'Date']]
    chart1 = chart1.loc[df['Date'] == '2021-11-19 00:00:00']
    a = chart1.groupby(['Stock Name','Sector']).count() ### gathers data by Lead 1
    a = a.groupby (['Sector']).count()
    industries = a.index
    industries = industries.tolist()
    
    a = a[share_measurement] ### data column that shows deal count
    a = a.rename('Count')
    a  = a.to_list()
    if select_central == 'Average':
        b = chart1.groupby(['Sector']).mean() ### gathers data by Lead 1
        b = b[share_measurement]
    
    else:
        b = chart1.groupby(['Sector']).median() ### gathers data by Lead 1
        b = b[share_measurement]
    
    b = b.to_list()
    fig = bar_chart(industries, a, b,"Sector Companies Count and " + select_central +' ' + share_measurement + ' as of ' + 'Nov 19, 2021', tickformat )
    st.plotly_chart(fig)
    st.write('Energy, Technology and Healthcare are the most on average % shorted stocks and average by $ value shorted stocks the past year. This suggests that healthcare and technology stocks are overvalued and overweighted due regulatory concerns. Energy due to the energy shortage.')
if sector == 'All':
    df = df ### healthcare data runs from 2018 while all IPO data runs from 2019
else:
    df = df.loc[df['Sector'] == sector]


with column_2:### Chart of distribution and Lead 1 Chart
    chart1 = df [['Aggregated Reportable Short Positions (HK$)','Share Shorted %', 'Stock Name', 'Industry', 'Date']]
    chart1 = chart1.loc[df['Date'] == '2021-11-19 00:00:00']

    a = chart1.groupby(['Stock Name','Industry']).count() ### gathers data by Lead 1
    a = a.groupby (['Industry']).count()
    industries = a.index
    industries = industries.tolist()
    
    a = a[share_measurement] ### data column that shows deal count
    a = a.rename('Count')
    a  = a.to_list()
    if select_central == 'Average':
        b = chart1.groupby(['Industry']).mean() ### gathers data by Lead 1
        b = b[share_measurement]
    
    else:
        b = chart1.groupby(['Industry']).median() ### gathers data by Lead 1
        b = b[share_measurement]
    
    b = b.to_list()
    fig = bar_chart(industries, a, b,sector +" Companies Count and " + select_central +' ' + share_measurement + ' as of ' + 'Nov 19, 2021', tickformat )
    st.plotly_chart(fig)
    st.write ('Health Information Services and Diagnostic and Research are among the top 3 for both % shorted stock and average $ value shorted the past year. Health Information Services only includes Yidu Tech and Ping An Good Doctor. Diagnostic & Research notably include Wuxi Apptec and Tigermed.')
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
      ['Hang Seng Healthcare', 'Hang Seng Index'])
'You selected: ', index

### Download HSH and HSI data
today = pd.to_datetime('today').strftime('%d/%m/%Y')
start = a.index[0].strftime('%d/%m/%Y')
end = a.index[-1].strftime('%d/%m/%Y')
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
fig.update_layout(title_text= sector + ' '+share_measurement + ' and ' + index + ' Performance')

# Set x-axis title
fig.update_xaxes(title_text="Date")

# Set y-axes titles
fig.update_yaxes(title_text= select_central + ' '+ share_measurement, secondary_y=False)
fig.update_yaxes(title_text="Index Level", secondary_y=True)
# fig.layout.yaxis.tickformat= '%0.'
st.plotly_chart(fig, use_container_width=True)
st.write('We can see a slight inverse relationship between the index and the % share shorted. Unrealistic steep drops in the % share shorted are due to new companies that report 0 shorted shares. Based on the trend line for the last 3 months, the healthcare sector looks heavily pessimistic. Energy, utilities, real estate, basic materials looks pessimistic. Consumer defensive, communication services, technology has been rather stable. Only financial services has been optimistic. This reflects the effects of a recovery, regulatory crackdowns and a energy shortage.')

######### make line chart on industry

industry = industries
industry = st.selectbox(
    'Which industry are you interested in?',
      industries)
'You selected: ', industry

### Download HSH and HSI data
performance = df.loc[df['Industry'] == industry]
performance = performance [['Date', 'Industry', 'Stock Name', share_measurement]]

if select_central == 'Average':
    a = performance.groupby(['Date']).mean()

else:
    a = performance.groupby(['Date']).median()
    
start = a.index[0].strftime('%d/%m/%Y')
end = a.index[-1].strftime('%d/%m/%Y')
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
fig.update_layout(title_text= industry + ' '+ share_measurement + ' and ' + index + ' performance')

# Set x-axis title
fig.update_xaxes(title_text="Date")

# Set y-axes titles
fig.update_yaxes(title_text= industry + ' '+ select_central + ' '+ share_measurement, secondary_y=False)
fig.update_yaxes(title_text="Index Level", secondary_y=True)
# fig.layout.yaxis.tickformat= '%0.'
st.plotly_chart(fig, use_container_width=True)

st.write('Health Information Services has had a steady upward trend. The steep drop from July 30th to August 6th is due to Yidu Tech being added to the % shorted dataset. Ignoring these effects and examining both companies individually, the price has steadily been declining while the share shorted % is steadily climbing.')
st.write('Interestingly, Diagnostics & Research has seen a steady decline in the average % share shorted whilst its share price has been steadily declining.')

########## line chart on company
performance = df [['Date', 'Stock Name', 'Yf Ticker', share_measurement]]

companies = performance['Stock Name']
companies = companies.tolist()
companies = list(dict.fromkeys(companies))
company = st.selectbox(
    'Which company are you interested in?',
      companies)
'You selected: ', company

performance = performance.loc[performance['Stock Name'] == company]
a = performance    
a.sort_values(by='Date', inplace=True)
a = a.set_index ('Date')
start = a.index[0].strftime('%Y-%m-%d')
end = a.index[-1].strftime('%Y-%m-%d')
ticker = a ['Yf Ticker']
ticker = ticker[0]

df_index = yf.download(ticker, start= start, end=end)

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(go.Scatter(x= a.index, y= a[share_measurement], name= select_central + ' '+ share_measurement),
    secondary_y=False)

fig.add_trace(go.Scatter(x = df_index.index, y= df_index['Adj Close'], name= company),
    secondary_y=True)
# Add figure title
fig.update_layout(title_text= company + ' ' + share_measurement + ' and ' + company + ' Stock Performance')

# Set x-axis title
fig.update_xaxes(title_text="Date")

# Set y-axes titles
fig.update_yaxes(title_text= industry + ' '+ select_central + ' '+ share_measurement, secondary_y=False)
fig.update_yaxes(title_text= company + " Adjusted Closing Price", secondary_y=True)
st.plotly_chart(fig, use_container_width=True)

df1 =     df.loc[df['Date'] == '2021-11-19 00:00:00']


if select_central == 'Average':
    df1 = df1.groupby(['Stock Name']).mean()

else:
    df1 = df1.groupby(['Stock Name']).median()
df1 = df1.iloc [:,:-2]
df1 = df1.drop('Stock Code', axis =1)
dict1 = df [['Stock Name', 'Industry']]

dict1 = dict1.drop_duplicates(subset=None, keep='first', inplace=False)

df1 = df1.merge(dict1, on='Stock Name', how='left')

st.write('Cansino Bio, the most % shares shorted, has seen steep % share shorted growth from Aug 6th to Aug 27th. There has been a corresponding drop in stock price since then.')
st.write('PA Good Doctor, the 2nd most % shares shorted as of Nov 19 has steadily been decreasing in price while its % share shorted has been steadily growing.')
st.write ('Wuxi Apptec, the 3rd most % shares shorted and the most aggregate $ value shorted, has had a non-inverse relationship reflecting the risky nature of its business and the various position of investors.')

st.write ('As of Nov 19, 2021')
df1

## Add a download button that gives the whole excel file. Just attach the link to github
## st.write("Download the full data file [link](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)")
