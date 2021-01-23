"""
The main operating file of the Portfolio Planner Dash App
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
import dash_bootstrap_components as dbc
import GBMconfidence as GBM
import plotly.graph_objects as go
import plotly.express as px

#Makes the default portfolio and csv file
table = pd.DataFrame({
    "Ticker":["AAPL","GE"],
    "Amount":[10000, 3500]
},index=range(2))
table.to_csv("dataTable.csv",index=False)

#Start of the web app configuration and layout
app = dash.Dash(__name__, prevent_initial_callbacks=False, external_stylesheets=[dbc.themes.LUX])
server = app.server

app.layout = dbc.Container(html.Div([


    dcc.Markdown('''
    # Portfolio planner

    ###### In this web app you can build custom portfolio and make projection of its expected returns, inspect its composition and view characteristics.

    #### How to use:
    1. Write the ticker of the asset and purchase amount you want to add/remove to given input fields. Site uses [yahoo finance](https://finance.yahoo.com) API,
    so you need to use tickers they use, like F = Ford Motor Company, FORTUM.HE = Fortum Oyj, TSLA = Tesla, Inc. and so on.

    2. After that you can use the buttons below to either add the chosen amount of given asset to your portfolio, remove given asset or clear the entire portfolio.

    3. When you are satisfied with your asset choises, it is time to choose how far into the future you want the projection made and the confidence level you prefer for it.
    Press CREATE PROJECTION and wait for the graphs to load. This may take couple seconds. 
    
    NOTE: if any of the tickers can't be found from yahoo an error message will be shown.

    '''),
    dbc.Row(dbc.Col(html.Div(["Stock ticker: ",
        dbc.Input(id="ticker",value="SPY",type= "text")]),
                width=12
    )),
    
    html.Div(["Purchase Amount: ",
        dbc.Input(id="purchaseAmount",value="10000",type= "text")]),

    dbc.Button(id='addAssetButton', n_clicks=0, children='Add Asset'),
    dbc.Button(id='deleteAssetButton', n_clicks=0, children='Delete Asset'),
    dbc.Button(id='clearButton', n_clicks=0, children='Clear Portfolio'),

    dcc.Markdown('''
    ###### Chosen assets:
    '''),
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

    html.Div(id="feedback"),
    

    dbc.Row([
        dbc.Col(dbc.Spinner(children=[dcc.Graph(id="graph")], color="success"),
                width=6),
        dbc.Col(dbc.Spinner(children=[dcc.Graph(id="pie-chart")], color="success"),
                width=6)
    ]),

    dbc.Row(dbc.Col(dbc.Spinner(children=[html.Div(id="breakdown")], color="success"),
                width=12)
    ),

    dcc.Markdown('''
    
    ###### The math

    1. Expected returns are based on Capital Asset Pricing Model. [AWCI](https://www.msci.com/acwi) is used as a market portfolio.

    2. Daily data from  [yahoo finance](https://finance.yahoo.com) is used for the calculations.

    3. Confidence levels follow log-normal distribution.

    
    @Teemu Saha.
    [LinkedIn](https://linkedin.com/in/teemu-saha-18090b19b)
    [GitHub](https://github.com/Tepes99)

    '''),




    
]),
fluid=True)

 
#Callback for the portfolio editing
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
    ticker = ticker.upper()
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

#Callback for the graphs and data table
@app.callback(
    Output(component_id= "graph", component_property= "figure"),
    Output(component_id= "breakdown", component_property= "children"),
    Output(component_id="pie-chart", component_property="figure"),
    Output(component_id= "feedback", component_property= "children"),
    [Input('createPortfolio', 'n_clicks'),
    State(component_id= "years", component_property= "value"),
    State(component_id= "confidence", component_property= "value")])


def updatePlot(update, years, confidence):

    df = pd.read_csv("dataTable.csv")                               #Reads the user inputted portfolio for
    listOfAssets = list(df.itertuples(index=False, name=None))      #the functions that calculate the data
    portfolio, notFoundAssets = cstm.callPortfolio(listOfAssets)    #for outputs
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
    #feedback to inform user of possible failure of data scraping
    if notFoundAssets != []:
        feedback = "`Error: Data for asset(s) with tickers {} could not be found, and are excluded from calculations.`".format(str(notFoundAssets))
    else:
        feedback = ""
    feedback = dcc.Markdown(feedback)
    portfolio.reset_index(inplace=True)
    portfolio = portfolio.rename(columns = {
        'index':'Ticker',
        'purchaseAmount':'Purchase Amount',
        'assetReturns':'Historical Returns',
        'assetCAPM':'Expected Returns',
        })
    del portfolio["indexReturns"]
    del portfolio["riskFreeRate"]
    return fig, dbc.Table.from_dataframe(
        portfolio,
        striped=True,
        bordered=True,
        hover=True,
        size='sm'
        ), pie, feedback

if __name__ == '__main__':
    app.run_server(debug=False)
