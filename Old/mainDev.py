"""
The main operating file of the Wealth Planner Dash App
"""
import pandas as pd
import numpy as np
import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import customAddIns as cstm



app = dash.Dash(__name__)



app.layout = html.Div([

    html.Div(["Initial investment: ",
        dcc.Input(id="investment",value="1",type= "number")]),
    
    html.Div(["Expected annual return: ",
        dcc.Input(id="growthRate",value="0",type= "number")]),
    
    html.Div(["Monthly investment: ",
        dcc.Input(id="monthlyPayment",value="0",type= "number")]),
    
    html.Div(["Asset Name: ",
        dcc.Input(id="assetName",value="Asset",type= "text")]),
    
    dcc.Graph(id="graph"),
])
@app.callback(
    Output(component_id= "graph", component_property= "figure"),
    [Input(component_id= "investment",component_property= "value"),
    Input(component_id= "growthRate",component_property= "value"),
    Input(component_id= "monthlyPayment",component_property= "value"),
    Input(component_id= "assetName",component_property= "value")]
)

def update(investment,growthRate,monthlyPayment,assetName):
    portfolio = cstm.createAsset(investment, growthRate, monthlyPayment,(2020,10,19),(2050,10,19),assetName)
    fig = px.line(portfolio, x = portfolio.index, y= assetName)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
