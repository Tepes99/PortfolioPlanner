import numpy as np

def GBM(currentPrice, expectedReturn, volatility, periodLenghtInYears, z):
    """
    Returns the mean, lower bound and higher bound for future price based on given parameters.
    """

    futurePriceLn = np.log(currentPrice) + (expectedReturn- (volatility**2)/2)*periodLenghtInYears
    
    confidenceIntervalLn = z*volatility*np.sqrt(periodLenghtInYears)

    futurePrice = np.exp(futurePriceLn)
    confidenceIntervalLow = np.exp(futurePriceLn - confidenceIntervalLn)
    confidenceIntervalHigh = np.exp(futurePriceLn + confidenceIntervalLn)

    return futurePrice, confidenceIntervalLow, confidenceIntervalHigh
#Example
#print(GBM(10,0.08,0.2,10,1.96))


def GBMP(currentPrice, expectedReturn, volatility, periodLenghtInYears, z):
    """
    Returns the mean, lower bound and higher bound for future prices based on given parameters.
    """
    expectedReturn = expectedReturn/100
    periodLenghtinDays = int(periodLenghtInYears*365.25)
 
    futurePricesLn = np.array([np.log(currentPrice)]*periodLenghtinDays)
    confidenceIntervalsLn = np.array([z*volatility] * periodLenghtinDays)
    futurePricesLn = futurePricesLn + (np.arange(1, periodLenghtinDays+1)/365.25)*(expectedReturn - (volatility**2)/2)
    confidenceIntervalsLn = confidenceIntervalsLn * np.sqrt(np.arange(1,periodLenghtinDays+1)/365.25)
    futurePrices = np.exp(futurePricesLn)
    confidenceIntervalLow = np.exp(futurePricesLn - confidenceIntervalsLn)
    confidenceIntervalHigh = np.exp(futurePricesLn + confidenceIntervalsLn)
    return futurePrices, confidenceIntervalLow, confidenceIntervalHigh

