from flask import Flask
server = Flask('my app')

# Standard imports
import datetime
import pandas as pd
import pytz
import json
import os
import random
import tweepy
from td.client import TDClient

# Dash imports
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Helper and config imports
import td_config
import td_helper
import reddit_config
import reddit_helper
import twitter_config
import twitter_helper

# Static data for testing
import static_data

# Setup table
symbols = td_helper.get_symbols()
df_quotes = td_helper.get_radar_quotes(symbols)

# Setup tweets table
try:
    df_tweets = twitter_helper.fetch_tweets(symbols)
except:
    df_tweets = pd.DataFrame({'Source': ['Please wait'], 'User': ['Twitter API rate limit'], 'Tweet': ['currently exceeded.']})

# # Setup reddit table
try:
    df_reddit = reddit_helper.get_reddit(reddit_config.client_id, reddit_config.client_secret, reddit_config.user_agent)
except:
    df_reddit = pd.DataFrame({'Date': ['Please wait'], 'User': ['Reddit API rate limit'], 'Tweet': ['currently exceeded.']})

# Initial chart one
df_cs_one = td_helper.get_radar_prices(1,5,df_quotes['Symbol'][random.randint(0,len(df_quotes['Symbol'])-1)])

fig_cs_one = go.Figure(data = [go.Candlestick(x=df_cs_one['Date'],
                                              open=df_cs_one['Open'],
                                              high=df_cs_one['High'],
                                              low=df_cs_one['Low'],
                                              close=df_cs_one['Close']),
                               go.Scatter(x = df_cs_one['Date'], y = df_cs_one['SMA_9'], line = dict(color = 'cyan', width = 1))])

fig_cs_one.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                         title_text='{} 5-minute Chart'.format(df_cs_one['Symbol'][0]), title_font_size = 20, #volatile_tickers[0]), title_font_size=20,
                         xaxis = dict(rangeslider = dict(visible = False)), showlegend = False)

fig_cs_one.update_xaxes(gridcolor = '#D2D2D2')


## App
app = dash.Dash('Dash Hello World', external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'], server = server)

text_style = dict(color='#444', fontFamily='sans-serif', fontWeight=300)

app.layout = html.Div([
    html.H1('RADAR WATCHLIST', style = {'textAlign': 'center', 'color': 'white'}),
    html.P('This application tracks all stock tickers of interest on a personal watchlist named "Radar". \nEvery 30-seconds this page will refresh with quotes for the tickers, a chart for the biggest gainer, and the latest tweets for all tickers.',
            style = {'textAlign': 'center', 'color': 'white', 'margin-top': '10px', 'margin-bottom': '10px'}),
    html.Div(dash_table.DataTable(
                id='table',
                columns = [{"name": i, "id": i} for i in df_quotes.columns],
                data = df_quotes.to_dict('records'),
                style_cell = {'textAlign': 'center', 'font_size': '20px'},
                style_data = {'backgroundColor': 'transparent', 'color': 'white'},
                style_header = {'backgroundColor': '#a1a1a1', 'color': 'black'},
                style_data_conditional=[{'if': {'filter_query': '{{Net Change}} > {}'.format(0),},'backgroundColor': '#4b9c69','color': 'white'},
                                        {'if': {'filter_query': '{{Net Change}} < {}'.format(0),},'backgroundColor': '#992525','color': 'white'},]),
        className = 'two columns'), # style = {'margin-top': '50px'}),#'width': '20%', 'display': 'inline-block', 'margin-left': '50px', }),
    html.Div(dcc.Graph(id = 'candle-one', figure = fig_cs_one), className = 'seven columns', style = {'margin-left': '250px'}), #, style = {'width': '30%', 'display': 'inline-block','margin-left': '100px','margin-top': '50px'}),
    html.Div(id = 'transport-value', style = {'display': 'none'}),
    html.Div(dash_table.DataTable(
                id='tweet-table',
                columns = [{"name": i, "id": i} for i in df_tweets.columns],
                data = df_tweets.to_dict('records'), style_data = {'backgroundColor': 'transparent', 'color': 'white'},
                style_header = {'backgroundColor': '#a1a1a1', 'color': 'black'},
                style_cell = {'textAlign': 'left', 'font_size': '13px', 'white-space': 'normal','word-wrap': 'break-word'}),
                className = 'five columns'),
    dcc.Interval(
        id = 'interval-component',
        interval = 30 * 1000,
        n_intervals = 0),
    html.Div(dash_table.DataTable(
        id='reddit-table',
        columns = [{"name": i, "id": i} for i in df_reddit.columns],
        data = df_reddit.to_dict('records'), style_data = {'backgroundColor': 'transparent', 'color': 'white', 'table-layout': 'fixed;'},
        style_header = {'backgroundColor': '#a1a1a1', 'color': 'black'}, style_cell = {'textAlign': 'center', 'font_size': '13px', 'white-space': 'normal','word-wrap': 'break-word',}), className = 'six columns'),
], style = {'margin-top': '50px', 'margin-left': '50px'})

@app.callback(Output('transport-value', 'children'), [Input('interval-component', 'n_intervals')])
def update_symbols(n):
    symbols = td_helper.get_symbols()
    return json.dumps(symbols)

@app.callback(Output('table', 'data'), [Input('transport-value', 'children')])
def update_table(j_symbols):
    df_quotes = td_helper.get_radar_quotes(json.loads(j_symbols)).to_dict('records')
    return df_quotes

@app.callback(Output('reddit-table', 'data'), [Input('transport-value', 'children')])
def update_reddit(n):
    try:
        df_reddit = reddit_helper.get_reddit(reddit_config.client_id, reddit_config.client_secret, reddit_config.user_agent).to_dict('records')
    except:
        df_reddit = pd.DataFrame({'title': ['Please wait'], 'score': ['Reddit API rate limit'], 'post': ['currently exceeded.']}).to_dict('records')
    return df_reddit

@app.callback(Output('tweet-table', 'data'), [Input('transport-value', 'children')])
def update_tweets(t_symbols):
    try:
        df_tweets = twitter_helper.fetch_tweets(json.loads(t_symbols)).to_dict('records')
    except:
        df_tweets = pd.DataFrame({'Source': ['Please wait'], 'User': ['Twitter API rate limit'], 'Tweet': ['currently exceeded.']}).to_dict('records')
    return df_tweets

@app.callback(Output("candle-one", "figure"), [Input('transport-value', 'children')])
def display_candlestick(j_symbols):
    tickers = td_helper.get_radar_quotes(json.loads(j_symbols))['Symbol']
    df_cs_one = td_helper.get_radar_prices(1, 5, tickers[random.randint(0, len(tickers) - 1)])

    fig_cs_one = go.Figure(data=[go.Candlestick(x=df_cs_one['Date'],
                                                open=df_cs_one['Open'],
                                                high=df_cs_one['High'],
                                                low=df_cs_one['Low'],
                                                close=df_cs_one['Close']),
                                 go.Scatter(x=df_cs_one['Date'], y=df_cs_one['SMA_9'],
                                            line=dict(color='cyan', width=1))])

    fig_cs_one.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                             title_text='{} 5-minute Chart'.format(df_cs_one['Symbol'][0]), title_font_size=20,
                             xaxis = dict(rangeslider = dict(visible = False)), showlegend = False)

    fig_cs_one.update_xaxes(gridcolor = '#D2D2D2')

    return fig_cs_one

if __name__ == '__main__':
    app.server.run()

#app.server.run(debug = True)