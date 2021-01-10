import pandas as pd


def combineDublicateTickers(df,ticker):
    
    if (len(df[((df.Ticker == ticker))].index)) > 0:
        dfi = df
        dfi = dfi.set_index("Ticker")
        if sum(list(map(int,dfi.loc[ticker,"Amount"])))>1:
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