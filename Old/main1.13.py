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
import test

app = dash.Dash(__name__, prevent_initial_callbacks=True)


app.layout = html.Div([

    html.Div(["Stock ticker: ",
        dcc.Input(id="ticker",value="SPY",type= "text")]),
    
    html.Div(["Purchase Amount: ",
        dcc.Input(id="purchaseAmount",value="10000",type= "text")]),

    html.Button(id='addAssetButton', n_clicks=0, children='Add Asset'),
    html.Button(id='deleteAssetButton', n_clicks=0, children='Delete Asset'),

    html.Div(id="components"),
    
    html.Button(id='createPortfolio', n_clicks=0, children='Create Portfolio'),

    dcc.Graph(id="graph"),
    html.Div(id="portfolioBreakdown")
    
])
@app.callback(
    Output(component_id= "components", component_property= "children"),
    [Input('addAssetButton', 'n_clicks')],
    [Input('deleteAssetButton', 'n_clicks')],
    [State(component_id= "ticker",component_property= "value"),
    State(component_id= "purchaseAmount",component_property= "value")]
)


def addAssetToList(add, delete, ticker, amount):
    assetList = pd.read_csv("dataTable.csv")

    #asset to be added
    asset = pd.DataFrame({
        "Ticker": ticker,
        "Amount": amount,
        },index=[len(assetList)])

    #Gets the users latest button pushed using dash callback context    
    ctx = dash.callback_context
    buttonPressed = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if buttonPressed == "addAssetButton":
        assetList = assetList.append(asset)
    else:
        assetList = cstm.deleteAsset(assetList,ticker)

    assetList = cstm.combineDublicateTickers(assetList, ticker)
    assetList.to_csv("dataTable.csv",index=False)

    return dash_table.DataTable(
        id="children",
        columns=[{"name": i, "id": i} for i in assetList.columns],
        data = assetList.to_dict('records')
        )

@app.callback(
    Output(component_id= "graph", component_property= "figure"),
    Output(component_id= "portfolioBreakdown", component_property= "children"),
    [Input('createPortfolio', 'n_clicks')])


def updatePlot(update):
    df = pd.read_csv("dataTable.csv")
    listOfAssets = list(df.itertuples(index=False, name=None))
    portfolio = cstm.callPortfolio(listOfAssets)
    growthRate = portfolio.loc["Portfolio","assetCAPM"]
    purchaseAmount = portfolio.loc["Portfolio","purchaseAmount"]
    graphData = cstm.createAsset(purchaseAmount, growthRate, 0, (2020,10,27),(2050,10,27), "Portfolio")
    fig = px.line(graphData, x = graphData.index, y= "Portfolio", title="Expected returns for the portfolio based on CAPM")
    
    portfolio.reset_index(inplace=True)
    portfolio = portfolio.rename(columns = {'index':'Ticker'})
    return fig, dash_table.DataTable(
        id="children",
        columns=[{"name": i, "id": i} for i in portfolio.columns],
        data = portfolio.to_dict('records')
        )


if __name__ == '__main__':
    app.run_server(debug=True)
