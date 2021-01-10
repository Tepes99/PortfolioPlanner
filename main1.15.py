"""
The main operating file of the Wealth Planner Dash App
"""
import pandas as pd
import numpy as np
import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.express as px
import customAddIns as cstm
import startup
import dash_bootstrap_components as dbc


startup.createDataTable()

app = dash.Dash(__name__, prevent_initial_callbacks=True, external_stylesheets=[dbc.themes.LUX])

app.layout = dbc.Container(html.Div([

    dbc.Row(dbc.Col(html.Div(["Stock ticker: ",
        dbc.Input(id="ticker",value="SPY",type= "text")]),
                width=12
    )),
    
    html.Div(["Purchase Amount: ",
        dbc.Input(id="purchaseAmount",value="10000",type= "text")]),

    dbc.Button(id='addAssetButton', n_clicks=0, children='Add Asset'),
    dbc.Button(id='deleteAssetButton', n_clicks=0, children='Delete Asset'),
    dbc.Button(id='clearButton', n_clicks=0, children='Clear Portfolio'),

    dbc.Row(dbc.Col(html.Div(id="components"),
                width=12
    )),
    dbc.Row(dbc.Col(html.Div(["Years: ",
        dbc.Input(id="years",value="10",type= "text")]),
                width=2
    )),
    dbc.Button(id='createPortfolio', n_clicks=0, children='Create Portfolio'),

    dbc.Row(dbc.Col(dcc.Graph(id="graph"),
                width=12
    )),

    dbc.Row(dbc.Col(html.Div(id="breakdown"),
                width=12
    )),



    
]),
fluid=True)

 

@app.callback(
    Output(component_id= "components", component_property= "children"),
    [Input('addAssetButton', 'n_clicks')],
    [Input('deleteAssetButton', 'n_clicks')],
    [Input('clearButton', 'n_clicks')],
    [State(component_id= "ticker",component_property= "value"),
    State(component_id= "purchaseAmount",component_property= "value")]
)


def addAssetToList(add, delete, clear, ticker, amount):
    assetList = pd.read_csv("dataTable.csv")

    #asset to be added
    asset = pd.DataFrame({
        "Ticker": ticker,
        "Amount": amount,
        },index=[len(assetList)])

    #Gets the users latest button pushed using dash callback context    
    ctx = dash.callback_context
    buttonPressed = ctx.triggered[0]['prop_id'].split('.')[0]
    
    #Button logic
    if buttonPressed == "addAssetButton":
        assetList = assetList.append(asset)
    if buttonPressed == "deleteAssetButton":
        assetList = cstm.deleteAsset(assetList,ticker)
    if buttonPressed == "clearButton":
        assetList = pd.DataFrame(columns=["Ticker","Amount"])
    
    assetList = cstm.combineDublicateTickers(assetList, ticker)
    assetList.to_csv("dataTable.csv",index=False)
    

    return dbc.Table.from_dataframe(
        assetList,
        striped=True,
        bordered=True,
        hover=True,
        size='sm'
        )

@app.callback(
    Output(component_id= "graph", component_property= "figure"),
    Output(component_id= "breakdown", component_property= "children"),
    [Input('createPortfolio', 'n_clicks'),
    State(component_id= "years", component_property= "value")])


def updatePlot(update, years):
    #reading and writing csv
    df = pd.read_csv("dataTable.csv")
    listOfAssets = list(df.itertuples(index=False, name=None))
    portfolio = cstm.callPortfolio(listOfAssets)
    growthRate = portfolio.loc["Portfolio","assetCAPM"]
    purchaseAmount = portfolio.loc["Portfolio","purchaseAmount"]
    #Date management an conversion from datetime object to tuple
    startDate = dt.datetime.now()
    endDate = str(startDate + dt.timedelta(days= int(years)*365))
    startDate = int(str(startDate)[0:4]), int(str(startDate)[5:7]), int(str(startDate)[8:10])
    endDate = int(endDate[0:4]), int(endDate[5:7]), int(endDate[8:10])
    #pulling graph data from yahoo and plotting
    graphData = cstm.createAsset(purchaseAmount, growthRate, 0, startDate, endDate, "Portfolio")
    fig = px.line(graphData, x = graphData.index, y= "Portfolio", title="Expected returns for the portfolio based on CAPM")
    portfolio.reset_index(inplace=True)
    portfolio = portfolio.rename(columns = {'index':'Ticker'})
    portfolio = portfolio.round(4)
    return fig, dbc.Table.from_dataframe(
        portfolio,
        striped=True,
        bordered=True,
        hover=True,
        size='sm'
        )

if __name__ == '__main__':
    app.run_server(debug=True)
