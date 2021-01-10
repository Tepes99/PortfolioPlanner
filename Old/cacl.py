def interestRateConverter(annualRate):

    """
    Converts inserted annual rate to daily compounding one
    """
    annualRate = annualRate*0.01
    annualRate = annualRate + 1
    annualRate = annualRate**(1/365.25)
    annualRate = annualRate - 1
    return annualRate