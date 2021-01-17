"""
Custom functions by Teemu Saha
"""

import pandas as pd
import numpy as np
import datetime as dt
import pandas_datareader.data as web

def interestRateConverter(annualRate):

    """
    Converts inserted annual rate to daily compounding one
    """
    dailyRate = annualRate*0.01
    dailyRate = dailyRate + 1
    dailyRate = dailyRate**(1/365.25)
    dailyRate = dailyRate - 1
    return dailyRate


#This function creates the dataframe for real estate assets for given period and growth rate in value
def createAsset(value, growthRate,monthlyPayment, startOfOwnership, endOfOwnership, assetName):
    """
    Returns pandas DataFrame for the given asset.

    value: float

    growthRate: float

    monthlyPayment: float

    assetName: str

    Dates: tuple (YYYY,MM,DD)

    Example: 
    House = createAsset(value= 100000,growthRate= 2,monthlyPayment= 200,startOfOwnership=(2020,10,18),endOfOwnership=(2020,11,18),assetName="House")

    """
    if value == str:
        value = 0.0
    #Setting the daterange user wants for the asset
    startOfOwnership = dt.datetime(*startOfOwnership)
    endOfOwnership = dt.datetime(*endOfOwnership)
    dates = pd.date_range(startOfOwnership,endOfOwnership).tolist()
    
    #Daily compunding interest rate
    dailyRate = interestRateConverter(growthRate)
    dailyRate += 1

    values = pd.Series([float(value)]*len(dates),index= dates)
    #DataFrame for the asset
    
    i = 1
    j = 0
    m = (365.25/12)
    while i < len(dates):
        
        values[i] = (values[i-1]*dailyRate)
        if j < int(i/m):
            values[i] += monthlyPayment
        j = int(i/m)
        i += 1
    
    #Values Series for the timeframe
    asset = pd.DataFrame({
    assetName: values
    })
    asset.index = dates
    asset.index.name = "Date"
    
    return asset



def getAsset(assetSymbol, fromDate, toDate):
    """
    Returns pandas Series object of the wanted asset from Yahoo

    assetSymbol: str

    fromDate: tuple (YYYY,MM,DD)

    toDate: tuple (YYYY,MM,DD)

    Example: TSLA = getAsset("TSLA", (2016,10,21), (2020,10,21))
    """
    fromDate = dt.datetime(*fromDate)
    toDate = dt.datetime(*toDate)

    asset = web.DataReader(assetSymbol, 'yahoo', fromDate, toDate)
    asset.rename(columns={"Adj Close":assetSymbol}, inplace= True)
    return asset[assetSymbol]


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

    
    ACWI.insert(1, assetSymbol, asset)  #data table including asset and ACWI
    dataTable = ACWI
    #Variables for calculating the beta
    volatilities = dataTable.pct_change().std()*np.sqrt(252)
    correlation = dataTable.corr().iloc[0,1]

    beta = correlation*(volatilities[1]/volatilities[0])
    
    assetPeriodLen = len(pd.date_range(assetStart,assetEnd))
    assetReturns = ((asset[-1]/asset[0])**(1/(assetPeriodLen/365.25))-1)*100    #Geometric Mean
    indexReturns = ((dataTable.iloc[-1,0]/dataTable.iloc[0,0])**(1/5)-1)*100              #Geometric Mean

    assetReturns = assetReturns + ((volatilities[1]**2)/2)  #Arithmetic mean
    indexReturns = indexReturns + ((volatilities[0]**2)/2)  #Arithmetic mean

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


def formPortfolio(assetList, assetsReturns):
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
        "Contribution":(portfolio["Contribution"]).sum()
    },index= ["Portfolio"])

    portfolio = portfolio.append(summary)


    return portfolio


def callPortfolio(assetList):
    """
    Calls portfolio from the list of assets and purchase amounts

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
    return formPortfolio(assets,assetsReturns)

def deleteAsset(df, ticker):
    """
    Delete asset from asset list of the site
    
    deleteAsset(df,"TSLA")
    """
    toDelete = df[((df.Ticker == ticker))].index
    df = df.drop(toDelete)
    return df

def combineDublicateTickers(df,ticker):
    """
    Combines values of same asset to one row on the dataframe
    """
    #FYI this is like the hackiest and dummest way of doing this probably
    if (len(df[((df.Ticker == ticker))].index)) > 0:
        dfi = df
        dfi = dfi.set_index("Ticker")
        if sum(list(map(int,dfi.loc[ticker,"Amount"])))>9:          
            amount = sum(list(map(int,dfi.loc[ticker,"Amount"])))
        else:
            amount = int(dfi.loc[ticker,"Amount"])
        df = df[df.Ticker != ticker]
        dfi= pd.DataFrame({
            "Ticker": ticker,
            "Amount": amount,
            },index=[len(dfi)])
        df = df.append(dfi)
    return df
"""
    if (len(df[((df.Ticker == ticker))].index)) > 0:
    #if ticker in df:
        dfi = df[df['Ticker'].str.contains(ticker)]["Amount"]
        print(dfi)
        dfi = list(dfi)
        dfi = list(map(int, dfi)) 
        df = df[df.Ticker != ticker]
        dfi= pd.DataFrame({
            "Ticker": ticker,
            "Amount": sum(dfi),
            },index=[len(df)])
        df = df.append(dfi)
    return df
"""