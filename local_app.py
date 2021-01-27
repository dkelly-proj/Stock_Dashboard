from flask import Flask
server = Flask('my app')

import dash
import dash_table
import pandas as pd
import datetime
import pytz
import json
import os
from td.client import TDClient
from config import account_number, client_id
import td_helper
import reddit_helper
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import twitter
import twitter_config

# Setup table
symbols = td_helper.get_symbols()
df_quotes = td_helper.get_radar_quotes(symbols)

# Setup tweets table
try:
    df_tweets = td_helper.fetch_tweets(tweet_symbols)
except:
    df_tweets = pd.DataFrame({'Date': ['Please wait'], 'User': ['Twitter API rate limit'], 'Tweet': ['currently exceeded.']})

# # Setup reddit table
try:
    df_reddit = reddit_helper.get_reddit()
except:
    df_reddit = pd.DataFrame({'Date': ['Please wait'], 'User': ['Reddit API rate limit'], 'Tweet': ['currently exceeded.']})
# Initial chart one
volatile_tickers = df_quotes['Symbol'][:2]
df_p_hist = td_helper.get_radar_prices(1,5,volatile_tickers)
df_cs_one = df_p_hist.query("Symbol == @volatile_tickers[0]").reset_index(drop=True)

fig_cs_one = go.Figure(go.Candlestick(x=df_cs_one['Date'], open=df_cs_one['Open'], high=df_cs_one['High'],
                                      low=df_cs_one['Low'], close=df_cs_one['Close']))

fig_cs_one.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                         title_text='{} 5-minute Chart'.format(volatile_tickers[0]), title_font_size=20,
                         xaxis = dict(rangeslider = dict(visible = False)))

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
                style_header = {'backgroundColor': '#a1a1a1', 'color': 'black'}, style_cell = {'textAlign': 'center', 'font_size': '13px'}), className = 'six columns'),
    dcc.Interval(
        id = 'interval-component',
        interval = 30 * 1000,
        n_intervals = 0
      html.Div(dash_table.DataTable(
                id='reddit-table',
                columns = [{"name": i, "id": i} for i in df_reddit.columns],
                data = df_reddit.to_dict('records'), style_data = {'backgroundColor': 'transparent', 'color': 'white', 'table-layout': 'fixed;'},
                style_header = {'backgroundColor': '#a1a1a1', 'color': 'black'}, style_cell = {'textAlign': 'center', 'font_size': '18px', 'white-space': 'normal','word-wrap': 'break-word',}), className = 'six columns'),
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
def update_reddit():
    try:
        df_reddit = reddit_helper.get_reddit().to_dict('records')
    except:
        df_reddit = pd.DataFrame({'Date': ['Please wait'], 'User': ['Reddit API rate limit'], 'Tweet': ['currently exceeded.']}).to_dict('records')
    return df_reddit

@app.callback(Output('tweet-table', 'data'), [Input('transport-value', 'children')])
def update_reddit():
    try:
        df_tweets = td_helper.fetch_tweets(tweet_symbols).to_dict('records')
    except:
        df_tweets = pd.DataFrame({'Date': ['Please wait'], 'User': ['Twitter API rate limit'], 'Tweet': ['currently exceeded.']}).to_dict('records')
    return df_tweets

@app.callback(Output("candle-one", "figure"), [Input('transport-value', 'children')])
def display_candlestick(j_symbols):
    volatile_tickers = td_helper.get_radar_quotes(json.loads(j_symbols))['Symbol'][:2]
    df_p_hist = td_helper.get_radar_prices(1,5,volatile_tickers)
    df_cs_one = df_p_hist.query("Symbol == @volatile_tickers[0]").reset_index(drop=True)

    fig_cs_one = go.Figure(go.Candlestick(x=df_cs_one['Date'], open=df_cs_one['Open'], high=df_cs_one['High'],
                                          low=df_cs_one['Low'], close=df_cs_one['Close']))

    fig_cs_one.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                             title_text='{} 5-minute Chart'.format(volatile_tickers[0]), title_font_size=20,
                             xaxis = dict(rangeslider = dict(visible = False)))

    fig_cs_one.update_xaxes(gridcolor = '#D2D2D2')

    return fig_cs_one

app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

if __name__ == '__main__':
    app.server.run()

#app.server.run(debug = True)