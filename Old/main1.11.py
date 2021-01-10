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
import plotly.express as px
import customAddIns as cstm



app = dash.Dash(__name__)



app.layout = html.Div([

    html.Div(["Stock ticker: ",
        dcc.Input(id="ticker",value="SPY",type= "text")]),
    
    html.Div(["Purchase Amount: ",
        dcc.Input(id="purchaseAmount",value="10000",type= "text")]),

    html.Button(id='submitButton', n_clicks=0, children='Submit'),
    
    dcc.Graph(id="graph"),
])
@app.callback(
    Output(component_id= "graph", component_property= "figure"),
    [Input('submitButton', 'n_clicks')],
    [State(component_id= "ticker",component_property= "value"),
    State(component_id= "purchaseAmount",component_property= "value")]
)

def updatePlot(update, ticker, purchaseAmount):
    portfolio = cstm.callPortfolio([(ticker,float(purchaseAmount))])
    growthRate = portfolio.loc["Portfolio","assetCAPM"]
    graphData = cstm.createAsset(purchaseAmount, growthRate, 0, (2020,10,27),(2050,10,27), ticker)
    fig = px.line(graphData, x = graphData.index, y= ticker, title="Expected returns for {} based on CAPM".format(ticker))
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
