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
import GBMconfidence as GBM
import plotly.graph_objects as go
import plotly.express as px


startup.createDataTable()

app = dash.Dash(__name__, prevent_initial_callbacks=True, external_stylesheets=[dbc.themes.LUX])
server = app.server

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
                width=3
    )),

    dbc.Row(dbc.Col(dcc.Dropdown(
        id='confidence',
        options=[
            {'label': 'Confidence level 50%', 'value': '50%'},
            {'label': 'Confidence level 90%', 'value': '90%'},
            {'label': 'Confidence level 95%', 'value': '95%'},
            {'label': 'Confidence level 99%', 'value': '99%'}
        ],
        value='90%'), width=3
    )),

    dbc.Button(id='createPortfolio', n_clicks=0, children='Create Projection'),

    

    dbc.Row([
        dbc.Col(dcc.Graph(id="graph"),
                width=6),
        dbc.Col(dcc.Graph(id="pie-chart"),
                width=6)
    ]),

    dbc.Row(dbc.Col(html.Div(id="breakdown"),
                width=12)
    ),
   




    
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
    Output(component_id="pie-chart", component_property="figure"),
    [Input('createPortfolio', 'n_clicks'),
    State(component_id= "years", component_property= "value"),
    State(component_id= "confidence", component_property= "value")])


def updatePlot(update, years, confidence):

    df = pd.read_csv("dataTable.csv")

    listOfAssets = list(df.itertuples(index=False, name=None))
    portfolio = cstm.callPortfolio(listOfAssets)
    growthRate = portfolio.loc["Portfolio","assetCAPM"]
    purchaseAmount = portfolio.loc["Portfolio","purchaseAmount"]
    volatility = portfolio.loc["Portfolio","volatility"]
    #dates
    startDate = dt.datetime.now()
    endDate = startDate + dt.timedelta(days= int(years)*365)
    #Confidence level
    if confidence == '50%':
        z = 0.675
    if confidence == '90%':
        z = 1.645
    if confidence == '95%':
        z = 1.960
    if confidence == '99%':
        z = 2.576
    #Projection based on geometric brownian motion
    futurePrices, confidenceIntervalLow, confidenceIntervalHigh = GBM.GBMP(purchaseAmount,growthRate,volatility,int(years),z)

    #plotting
    x = pd.date_range(startDate,endDate).tolist()
    x_rev = x[::-1]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x= x+x_rev,
        y=list(confidenceIntervalLow)+list(futurePrices)[::-1],
        fill='toself',
        fillcolor='rgba(100,0,0,0.2)',
        line_color='rgba(255,255,255,0)',
        showlegend=False,
        name= confidence +'Confidence level',
    ))

    fig.add_trace(go.Scatter(
        x= x+x_rev,
        y=list(confidenceIntervalHigh)+list(futurePrices)[::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line_color='rgba(255,255,255,0)',
        showlegend=False,
        name= confidence +'Confidence level',
    ))

    fig.add_trace(go.Scatter(
        x=x, y=futurePrices,
        line_color='rgb(0,100,80)',
        name='Portfolio',
    ))

    fig.add_trace(go.Scatter(
        x=x, y=confidenceIntervalLow,
        line_color='rgb(200,0,0)',
        name='Lower bound',
    ))

    fig.add_trace(go.Scatter(
        x=x, y=confidenceIntervalHigh,
        line_color='rgb(0,200,160)',
        name='Upper bound',
    ))

    fig.update_traces(mode='lines')

    portfolio = portfolio.round(4)
    pieData = portfolio.iloc[:-1,:]

    """
    pie = px.pie(
        pieData,
        labels= pieData.index,
        values= "Contribution",
        hover_name= pieData.index,
        hover_data= ["assetCAPM", "volatility"],
        custom_data= ["assetCAPM", "volatility"],
        #custom_data=["assetCAPM", "volatility", "beta"],
        title= "Portfolio composition",
    )
    
    
    """
    pie = go.Figure(go.Pie(
        name = "Portfolio composition",
        values = pieData['Contribution'],
        labels = pieData['volatility']*100,
        showlegend= False,
        #hover_data= ['assetCAPM', 'volatility', 'beta'],
        customdata= pieData['assetCAPM'],
        text= pieData.index,
        hole= 0.5,
        hovertemplate = "Expected return:%{customdata}: <br>Contribution: %{value} </br>Volatility:%{label}<br>Ticker:%{text}",
        
    ))
    
    portfolio.reset_index(inplace=True)
    portfolio = portfolio.rename(columns = {'index':'Ticker'})
    return fig, dbc.Table.from_dataframe(
        portfolio,
        striped=True,
        bordered=True,
        hover=True,
        size='sm'
        ), pie

if __name__ == '__main__':
    app.run_server(debug=True)
