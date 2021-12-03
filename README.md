# HKEX_shortsell
Follow link to access the app: https://share.streamlit.io/epiphronquant/hkex_shortsell/main/HKEX_Short_Positions_App.py

Click, drag, and have fun


**Key Assumptions**

1. Total shares used as denominator for Share Shorted % uses the most recent data on the HKEX website
2. For dual class shares, total shares outstanding only refers to the component listed
3. We only examine companies that are still listed on HKEX
4. We do NOT examine ETFs
5. We do NOT examine stocks on the NASDAQ-AMEX pilot program
6. Market Cap is of November 24th

**Data Sources**

1. _SFC_: Date, Stock Code, Stock Name, Aggregated Reportable Short Positions (Shares), Aggregated Reportable Short Positions (HK$) 
https://www.sfc.hk/en/Regulatory-functions/Market/Short-position-reporting/Aggregated-reportable-short-positions-of-specified-shares 

2. _Yahoo Finance_: Sector, Industry, Market Cap

3. _HKEX_ (various links found in data file): Shares Outstanding, Stock Name CN, 

**Chart by Chart Explanation**

**1. Sector Company Count and (_Average or Median_) (_Share % Shorted or Aggregate Reportable Share Positions (HK$)_) as of _Date_**

Examining ONLY the latest available SFC data. The blue bar counts the amount of companies in the respective sector. The red bar takes the average/median of the Share % Shorted/Aggregate Reportable Share Positions for companies in the respective sector. 

**2. _Sector_ companies count and (_Average or Median_) (_Share % Shorted or Aggregate Reportable Share Positions (HK$)_) as of _Date_**

Examining ONLY the latest available SFC data. The blue bar counts the amount of companies in the selected sector. The red bar takes the average/median of the Share % Shorted/Aggregate Reportable Share Positions for companies in the respective industry. 

**3. _Sector_ (_Share % Shorted or Aggregate Reportable Share Positions (HK$)_) and (_Hang Seng Healthcare or Hang Seng Index_) Chart**

The blue line represents the average/median of all companies Share % Shorted/Aggregate Reportable Share Positions in the selected sector over time. The red line represents the index level change over time.

**4. _Industry_ (_Share % Shorted or Aggregate Reportable Share Positions (HK$)_) and (_Hang Seng Healthcare or Hang Seng Index_) Chart**

The blue line represents the average/median of all companies Share % Shorted/Aggregate Reportable Share Positions in the selected industry over time. The red line represents the index level change over time.

**5. Chart Display**

The chart displays the SFC most recent data by Share Shorted % ranked on top. This lets us see which companies are the most shorted that we can then select below. The chart is highly interactable and by clicking on the headers we can rank the data.

**6. _Company_ (_Share % Shorted or Aggregate Reportable Share Positions (HK$)_) and _Company_ Stock Chart**

The blue line represents the reported Share % Shorted/Aggregate Reportable Share Positions in the company over time. The red line represents its stock performance over time.
