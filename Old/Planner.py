import pandas as pd
import numpy as np
import datetime as dt
from cacl import interestRateConverter

#This function creates the dataframe for real estate assets for given period and growth rate in value
def createAsset(value, growthRate, startOfOwnership, endOfOwnership, assetName):
    """
    Returns pandas DataFrame for the given asset.

    value: float

    growthRate: float

    assetName: str

    Dates format tuple: (YYYY,MM,DD)
    """
    #Setting the daterange user wants for the asset
    startOfOwnership = dt.datetime(*startOfOwnership)
    endOfOwnership = dt.datetime(*endOfOwnership)
    dates = pd.date_range(startOfOwnership,endOfOwnership).tolist()

    #Daily compunding interest rate
    dailyRate = interestRateConverter(growthRate)
    dailyRate += 1


    growthMultipliers = pd.Series([dailyRate]*len(dates))

    i = 0
    while i < len(dates):
        growthMultipliers[i] = growthMultipliers[i]**i
        i += 1

    #Loop for the cumulative products used in multiplication
    #growthMultipliers = growthMultipliers.cumprod()
    #Values Series for the timeframe
    values = pd.Series([value]*len(dates))
    values = values.mul(growthMultipliers)

    asset = pd.DataFrame({
    assetName: values
    })
    asset.index = dates
    return asset

House = createAsset(value= 100000,growthRate= 2,startOfOwnership=(2020,10,18),endOfOwnership=(2024,10,18),assetName="House")

print(House)
