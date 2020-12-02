# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 15:07:15 2019

@author: harshit.mahajan
"""
# Calculate VaR for individual portfolio

import pandas as pd 
import numpy as np 
from scipy.stats import norm 

filename = 'XXX'
excelFile = pd.ExcelFile(filename)
sheetList = excelFile.sheet_names

#Actual Prices
actualPrices = excelFile.parse('Actual_Px', header = None)
actualPrices =  actualPrices.iloc[6:,1:5].reset_index(drop = True)
actualPrices.columns = ['Date', 'WTI','Brent','NG']
actualPrices = actualPrices.drop(actualPrices.index[0])

production = excelFile.parse('Production', header = None)
production  =  production.iloc[2:,:].reset_index(drop = True)
production.columns =  ['Date','WTI','Brent','HHB','NBP','NGL']

revenue = excelFile.parse('Revenue', header = None)
revenue.columns = revenue.iloc[0]
revenue= revenue.drop(revenue.index[0])

revenue = pd.merge(revenue, actualPrices, left_on = 'Date', right_on = 'Date', how = 'left').fillna(method = 'ffill').reset_index(drop=True)
revenue['WTIR']  = revenue['WTI_x'] * revenue['WTI_y']
revenue['BrentR'] = revenue['BRT'] * revenue['Brent']
revenue['GasR'] =  revenue['HHB'] * revenue['NG']
revenue['sum'] = revenue['WTIR'] + revenue['BrentR'] + revenue['GasR']

revenue['wtiWeight'] = revenue['WTIR']/revenue['sum']
revenue['brentWeight'] = revenue['BrentR']/revenue['sum']
revenue['gasWeight'] = revenue['GasR']/revenue['sum']

startDate = '2011-01-01'
endDate = ' 2011-02-01' 
dateRange = pd.date_range(startDate,endDate). tolist()

portMean = []
portStd = []
oneDayvar = []
annualVar = []
dateId = []
portReturn = []

conf_level = 1-0.05

for date in dateRange:
    print(date)
    dateId.append(date)
    tempPrices = actualPrices[(actualPrices['Date'] > date - 500) & (actualPrices['Date'] < date)]
    tempReturns = np.log(tempPrices.iloc[1:,1:4].astype(float).dropna()/tempPrices.iloc[1:,1:4].shift(1).astype(float).dropna())
    tempReturnsLast =  tempReturns.iloc[-1,:] 
    cov_matrix = tempReturns.cov() 
#    tempReturns[tempReturns['Brent].cov() 
    mean_returns = tempReturns.mean()
    tempRev = revenue[revenue['Date']  == date].reset_index(drop=True)
    weights = np.array([tempRev['wtiWeight'],tempRev['brentWeight'],tempRev['gasWeight']])
    port_mean = mean_returns.dot(weights).item()*252
    portMean.append(port_mean)
    port_stdev = np.sqrt(weights.T.dot(cov_matrix).dot(weights)).item()
    portStd.append(port_stdev)
    #one_day_var = norm.ppf(conf_level, port_mean, port_stdev) 
    oneDayvar.append(norm.ppf(conf_level, port_mean, port_stdev))
    annualVar.append(norm.ppf(conf_level, port_mean, port_stdev)* np.sqrt(252))
    portReturn.append(tempReturnsLast.dot(weights).item())
    
    #Component VaR
    #tempReturns.dot(weights).cumprod().plot()
    #.Portfolio.plot()

df = pd.DataFrame({'dateId':dateId,'portMean': portMean,'portStd': portStd,'oneDayvar':oneDayvar,'annualVar':annualVar,
                   'portReturn': portReturn})
