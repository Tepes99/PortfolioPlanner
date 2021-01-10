"""
Scrapes market data from yahoo
"""

import datetime as dt
import pandas_datareader.data as web
import pandas as pd
import numpy as np

def addAsset(assetSymbol, purchaseAmount): #, fromDate, toDate):
    """
    Returns assets volatility and expected return for given period

    assetSymbol: str

    purchaseAmount: float or integer

    Example: TSLA = getAsset("TSLA", 1000)

    Returns: assetSymbol, purchaseAmount, assetReturns, indexReturns, assetCAPM, beta, riskFreeRate
    """

    #Dates for scraping the historical data from Yahoo for the asset and MCSI All World Index ETF
    end = dt.datetime.now()
    start = end + dt.timedelta(days= -5*365.25)

    #Asset data scraping
    asset = web.DataReader(assetSymbol, 'yahoo', start, end)
    asset.rename(columns={"Adj Close":assetSymbol}, inplace= True)
    asset = asset[assetSymbol]
    assetReturnsList = asset.pct_change()

    assetDates = list(asset.index)
    assetStart = assetDates[0]
    assetEnd = assetDates[-1]
    #Market Index data scraping
    ACWI = web.DataReader("ACWI", 'yahoo', start, end)
    ACWI.rename(columns={"Adj Close":"ACWI"}, inplace= True)
    ACWI = pd.DataFrame(ACWI["ACWI"])

    #Risk free rate as 13-Week US Treasury
    riskFreeRate = web.DataReader("^IRX", 'yahoo', end+dt.timedelta(days= -5) , end)
    riskFreeRate.rename(columns={"Adj Close":"Risk Free Rate"}, inplace= True)
    riskFreeRate = float(pd.DataFrame(riskFreeRate["Risk Free Rate"]).iloc[-1])

    ACWI.insert(1, assetSymbol, asset)

    #Variables for calculating the beta
    volatilities = ACWI.pct_change().std()*np.sqrt(252)
    correlation = ACWI.corr().iloc[0,1]

    beta = correlation*(volatilities[1]/volatilities[0])
    
    assetPeriodLen = len(pd.date_range(assetStart,assetEnd))
    assetReturns = ((asset[-1]/asset[0])**(1/(assetPeriodLen/365.25))-1)*100
    indexReturns = ((ACWI.iloc[-1,0]/ACWI.iloc[0,0])**(1/5)-1)*100

    assetCAPM = beta*(indexReturns-riskFreeRate) + riskFreeRate
    
    asset = pd.DataFrame({
        "purchaseAmount":purchaseAmount,
        "assetReturns":assetReturns,
        "volatility": volatilities[1],
        "indexReturns":indexReturns,
        "assetCAPM":assetCAPM,
        "beta":beta,
        "riskFreeRate":riskFreeRate
    },index= [assetSymbol])
    return asset, assetReturnsList


def callPortfolio(assetList, assetsReturns):
    """
    Forms portfolio from a list of assets that are made by addAsset function
    """

    portfolio = pd.DataFrame(columns= ("purchaseAmount", "assetReturns","volatility", "indexReturns", "assetCAPM", "beta", "riskFreeRate"))
    for asset in assetList:
        portfolio = portfolio.append(asset, ignore_index= False)
    
    portfolio["Contribution"] = (portfolio["purchaseAmount"] / portfolio["purchaseAmount"].sum())
    
    #Calculating the portfolio volatility
    covarianceMatrix = assetsReturns.cov()
    weights = portfolio["Contribution"]
    portfolioVol = np.sqrt(weights.T.dot(covarianceMatrix).dot(weights))*np.sqrt(252)
    
    summary = pd.DataFrame({
        "purchaseAmount":portfolio["purchaseAmount"].sum(),
        "assetReturns":(portfolio["assetReturns"]*portfolio["Contribution"]).sum(),
        "volatility":portfolioVol,
        "indexReturns":(portfolio["indexReturns"]*portfolio["Contribution"]).sum(),
        "assetCAPM":(portfolio["assetCAPM"]*portfolio["Contribution"]).sum(),
        "beta":(portfolio["beta"]*portfolio["Contribution"]).sum(),
        "riskFreeRate":(portfolio["riskFreeRate"]*portfolio["Contribution"]).sum(),
        "Contribution": (portfolio["Contribution"]).sum()
    },index= ["Portfolio"])

    portfolio = portfolio.append(summary)


    return portfolio


def formPortfolio(assetList):
    """
    Forms portfolio from the list of assets and purchase amounts

    Example:

    assetList = [
    ("FB", 50),
    ("AAPL",50),
    ("MSFT", 50)
    ]
    """
    assets=[]
    assetsReturns=pd.DataFrame()
    for asset in assetList:
        asset, assetReturnsList = addAsset(*asset)
        assets.append(asset)
        assetsReturns.insert(0,assetReturnsList.name,assetReturnsList)
    return callPortfolio(assets,assetsReturns)

#print(formPortfolio(assetList))



