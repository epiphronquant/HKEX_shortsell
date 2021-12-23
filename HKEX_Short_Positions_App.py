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
from streamlit.ScriptRunner import RerunException
raise RerunException
st.set_page_config(layout="wide")
st.title('HKEX Short Positions')

@st.cache
def load_data(link):
    df = pd.read_excel(link,sheet_name='Sheet1', header = 0, engine = 'openpyxl', parse_dates = False)
    df = df.loc[df['Listed?'] == 1] ### Filters rows where it is still listed
    df = df.loc[df['ETF?'] == 0] ### Filters rows where it is not an ETF
    df = df.loc[df['Stock Name'].str[-2:] != '-T'] ### Filters out stocks which are trading only under the NASDAQ-AMEX pilot program
    df['Date']= pd.to_datetime(df['Date'], dayfirst = True)### converts Date column to datetime variable
    return df
link = r'SFC.xlsx'
df = load_data(link)
st.write('**Ping An Good Doctor, Cansino Bio and Wuxi Apptec are the 3 most shorted healthcare stocks on the SEHK. PA Good Doctor and Cansino have a worrying increase in short selling whilst Wuxi Apptec reflects normal market speculation. There are evident effects in the stock market of a recovery, regulatory crackdowns and energy shortage.**')
st.write('**Key Assumptions: **')
st.write('**Total shares used as denominator for Share Shorted % uses the most recent data on the HKEX website.**')
st.write('**For dual class shares, shares outstanding only refers to the component listed**')
st.write('**We only examine companies that are still listed on HKEX**')
st.write ('All assumptions and further info can be found in [documentation](https://github.com/epiphronquant/HKEX_shortsell)')
### mkt cap sliding filter
slider = st.slider("Select Market Cap in HKD 100's of million", min_value=0, value=(0,50000) ,max_value=50000)
slider = tuple([100000000*x for x in slider])
df = df[df['Market Cap (Nov 24)'].between(slider [0], slider [1])]

column_1, column_2 = st.columns(2) ### Divides page into 2 columns
with column_1:## dropdown for share measurement
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
        chart1 = chart1.loc[df['Date'] == '2021-12-03 00:00:00']
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
        fig = bar_chart(industries, a, b,"Sector Companies Count and " + select_central +' ' + share_measurement + ' as of ' + 'Nov 26, 2021' )
        return fig  
    fig = chart_1(df, share_measurement, select_central)    
    st.plotly_chart(fig)

    st.write('Interpretation: Real Estate has 136 companies that can be shorted. On average, 1% of their outstanding shares are shorted.')
    st.write('Energy, Technology and Healthcare are the most on average % shorted stocks and average by $ value shorted stocks on Nov 26. This suggests that healthcare and technology stocks are overvalued and overweighted due regulatory concerns. Energy due to the energy shortage.')

if sector == 'All':
    df = df 
else:
    df = df.loc[df['Sector'] == sector]

with column_2:### Industry Chart
    chart1 = df [['Aggregated Reportable Short Positions (HK$)','Share Shorted %', 'Stock Name', 'Industry', 'Date']]
    chart1 = chart1.loc[df['Date'] == '2021-12-03 00:00:00']

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
    fig = bar_chart(industries, a, b,sector +' Sub Sector' +" Companies Count and " + select_central +' ' + share_measurement + ' as of ' + 'Nov 26, 2021')

    st.plotly_chart(fig)
    st.write ('Interpretation: There are 36 biotech companies that can be shorted. An average of 1.6% of their shares are shorted. ')
    st.write ('Health Information Services and Diagnostic and Research are among the top 3 for both % shorted stock and average $ value shorted on Nov 26. Health Information Services only includes Yidu Tech and Ping An Good Doctor. Diagnostic & Research notably include Wuxi Apptec and Tigermed.')
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

    #Download HSH and HSI data
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
fig.update_layout(title_text= sector + ' '+share_measurement + ' and ' + index + ' Chart')
    # Set x-axis title
fig.update_xaxes(title_text="Date")
    # Set y-axes titles
fig.update_yaxes(title_text= sector+ ' ' + select_central + ' '+ share_measurement, secondary_y=False)
fig.update_yaxes(title_text= index + ' '+ "Level", secondary_y=True)
st.plotly_chart(fig, use_container_width=True)
st.write('Interpretation: In 2021, the healthcare sectors average share shorted ranges from 1.7% to 2.1%. The Hang Seng healthcare index ranged from 8,362 points to 5,099 ponits.')
st.write('We can see a slight inverse relationship between the index and the % share shorted. Unrealistic steep drops in the % share shorted are due to new companies that report 0 shorted shares. Based on the trend line for the last 3 months, the healthcare sector looks heavily pessimistic. Energy, utilities, real estate, basic materials looks pessimistic. Consumer defensive, communication services, technology has been rather stable. Only financial services has been optimistic. This reflects the effects of a recovery, regulatory crackdowns and a energy shortage.')

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
fig.update_layout(title_text= industry + ' '+ share_measurement + ' and ' + index + ' Chart')
    # Set x-axis title
fig.update_xaxes(title_text="Date")
    # Set y-axes titles
fig.update_yaxes(title_text= industry + ' '+ select_central + ' '+ share_measurement, secondary_y=False)
fig.update_yaxes(title_text="Index Level", secondary_y=True)
st.plotly_chart(fig, use_container_width=True)

st.write('Interpretation: In 2021, the biotech index average share shorted ranged from 1.1% to 1.6%. The Hang Seng healthcare index ranged from 8,362 points to 5,099 ponits.')
st.write('Health Information Services has had a steady upward trend. The steep drop from July 30th to August 6th is due to Yidu Tech being added to the % shorted dataset. Ignoring these effects and examining both companies individually, the price has steadily been declining while the share shorted % is steadily climbing.')
st.write('Interestingly, Diagnostics & Research has seen a steady decline in the average % share shorted whilst its share price has been steadily declining.')

########## chart displaying key information of raw data
df1 = df.loc[df['Date'] == '2021-12-03 00:00:00']

@st.cache()
def chart_5(df1, select_central, sector):
    if select_central == 'Average':
        df1 = df1.groupby(['Stock Name']).mean()
    
    else:
        df1 = df1.groupby(['Stock Name']).median()
    df1 = df1.iloc [:,:-2]
    df1 = df1.drop(['Aggregated Reportable Short Positions (Shares)', 'Shares Outstanding'], axis =1)
    dict1 = df [['Stock Name', 'Stock Name CN','Industry']]
    
    dict1 = dict1.drop_duplicates(subset=None, keep='first', inplace=False)
    
    df1 = df1.merge(dict1, on='Stock Name', how='left')
    column_name = ["Stock Name", "Stock Name CN", "Stock Code", "Aggregated Reportable Short Positions (HK$)", "Share Shorted %", "Market Cap (Nov 24)", "Industry"]
    df1 = df1.reindex(columns=column_name)
    df1 ['Stock Code'] = df1['Stock Code'].astype(int)
    df1 = df1.sort_values(by=['Share Shorted %'], ascending = False)
    return df1
st.write('')
st.write ('Chart below only shows short data from Nov 26, 2021')
df1 = chart_5(df1, select_central, sector)
df1

########## line chart on company
performance = df [['Date', 'Stock Name', 'Yf Ticker', share_measurement]]

companies = performance['Stock Name']
companies = companies.tolist()
companies = list(dict.fromkeys(companies))
company = st.selectbox(
    'Which company are you interested in?',
      companies)
'You selected: ', company

@st.cache(suppress_st_warning=False, allow_output_mutation=True)
def chart_6 (performance, company, share_measurement, sector):
    performance = performance.loc[performance['Stock Name'] == company]
    a = performance    
    a.sort_values(by='Date', inplace=True)
    a = a.set_index ('Date')
    start = a.index[0].strftime('%Y-%m-%d')
    end = a.index[-1]
    end = end + pd.DateOffset(1)
    end = end.strftime('%Y-%m-%d')
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
    fig.update_layout(title_text= company + ' ' + share_measurement + ' and ' + company + ' Stock Chart')
    # Set x-axis title
    fig.update_xaxes(title_text="Date")
    # Set y-axes titles
    fig.update_yaxes(title_text= company + ' '+ share_measurement, secondary_y=False)
    fig.update_yaxes(title_text= company + " Adjusted Closing Price (HKD)", secondary_y=True)
    return fig
fig = chart_6(performance, company, share_measurement, sector)
st.plotly_chart(fig, use_container_width=True)

st.write('Interpretation: In 2021, Hutchmeds shorted ranged from 0% to 0.2%. Hutchmeds adjusted close price ranged from 66 HKD to 45 HKD.')
st.write('PA Good Doctor, the most % shares shorted as of Nov 26 has steadily been decreasing in price while its % share shorted has been steadily growing.')
st.write('Cansino Bio, the 2nd most % shares shorted, has seen steep % share shorted growth from Aug 6th to Aug 27th. There has been a corresponding drop in stock price since then.')
st.write ('Wuxi Apptec, the 3rd most % shares shorted and the most aggregate $ value shorted, has had a non-inverse relationship reflecting the risky nature of its business and the various position of investors.')

## Link to github where you can download the file
st.write("[Download the full data file](https://github.com/epiphronquant/HKEX_shortsell/raw/main/SFC.xlsx)")
