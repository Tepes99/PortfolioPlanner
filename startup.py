import os
import pandas as pd

def createDataTable():
    table = pd.DataFrame(columns=["Ticker","Amount"])
    table.to_csv("dataTable.csv",index=False)
    
createDataTable()