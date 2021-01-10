import pandas as pd

df = pd.read_csv("dataTable.csv")
print(df)
def combineDublicateTickers(df,ticker):
    #dfi = pd.DataFrame()
    if (len(df[((df.Ticker == ticker))].index)) > 0:
        dfi = df[df['Ticker'].str.contains(ticker)]["Amount"]
        df = df[df.Ticker != ticker]
        dfi= pd.DataFrame({
            "Ticker": ticker,
            "Amount": dfi.sum(),
            },index=[len(df)])
        df = df.append(dfi)
    return df

df = combineDublicateTickers(df, "SPY")
print(df)
