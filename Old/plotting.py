import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px
import customAddIns as cstm

def updatePlot(ticker, purchaseAmount):
    portfolio = cstm.callPortfolio([(ticker,purchaseAmount)])
    growthRate = portfolio.loc["Portfolio","assetCAPM"]
    graphData = cstm.createAsset(purchaseAmount, growthRate, 0, (2020,10,19),(2050,10,19), ticker)
    fig = px.line(graphData, x = graphData.index, y= ticker)
    return fig.show()

updatePlot("TSLA", 1000)