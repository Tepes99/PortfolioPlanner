"""
The main operating file of the Wealth Planner Dash App
"""
import pandas as pd
import numpy as np
import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import customAddIns as cstm



app = dash.Dash(__name__)

portfolio = cstm.createAsset(5000, 7, 100,(2020,10,19),(2050,10,19),"Portfolio")

fig = px.line(portfolio, x = portfolio.index, y="Portfolio")

app.layout = html.Div(children=[
    html.H1(children='Portfolio'),

    html.Div(children='''
        Portfolio value over time
        '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
