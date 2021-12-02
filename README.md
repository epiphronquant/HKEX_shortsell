# HKEX_shortsell
Follow link to access the app: https://share.streamlit.io/epiphronquant/hkex_shortsell/main/HKEX_Short_Positions_App.py

**Key Assumptions**

1. Total shares used as denominator for Share Shorted % uses the most recent data on the HKEX website
2. For dual class shares, total shares outstanding only refers to the component listed
3. We only examine companies that are still listed on HKEX
4. We do NOT examine ETFs
5. We do NOT examine stocks on the NASDAQ-AMEX pilot program
6. Market Cap is of November 24th

**Data Sources**

**SFC**: Date, Stock Code, Stock Name, Aggregated Reportable Short Positions (Shares), Aggregated Reportable Short Positions (HK$) 
https://www.sfc.hk/en/Regulatory-functions/Market/Short-position-reporting/Aggregated-reportable-short-positions-of-specified-shares 

**Yahoo Finance**: Sector, Industry, Market Cap

**HKEX** (various links found in data file): Shares Outstanding, Stock Name CN, 

**Chart by Chart Explanation**

Sector Company Count and _Average or Median_ _Share % Shorted or Aggregate Reportable Share Positions (HK$)_

The blue bar counts the amount of companies in the respective sector. The red bar takes the average/median of the Share % Shorted/Aggregate Reportable Share Positions for companies in the respective sector.

