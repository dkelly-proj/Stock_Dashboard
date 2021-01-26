import datetime
import pandas as pd
import pytz
from td.client import TDClient
from config import account_number, pwd, client_id
import twitter
import twitter_config

# retrieve symbols from Radar watchlist
def get_symbols():
    TDSession = TDClient(
        client_id=client_id,
        redirect_uri='http://localhost/test',
        credentials_path='td_state.json')

    TDSession.login()

    response = TDSession.get_watchlist_accounts()

    i = 0

    for r in response:
        if r['name'] == 'Radar':
            watch = response[i]
            symbols = [watch['watchlistItems'][x]['instrument']['symbol'] for x in range(len(watch['watchlistItems']))]
        else:
            i += 1
            
    return symbols

# get current quotes for Radar watchlist symbols
def get_radar_quotes(symbol_list):
    TDSession = TDClient(
        client_id=client_id,
        redirect_uri='http://localhost/test',
        credentials_path='td_state.json')

    TDSession.login()
    
    quotes = TDSession.get_quotes(symbol_list)
    
    sym = []
    last = []
    net = []
    per = []

    for quote in quotes:
        sym.append(quotes[quote]['symbol'])
        last.append(quotes[quote]['lastPrice'])
        net.append(quotes[quote]['netChange'])
        per.append(quotes[quote]['netPercentChangeInDouble'])

    df_quotes = (pd.DataFrame({'Symbol': sym, 'Last Price': last, 'Net Change': net, 'Net % Change': per}))
    df_quotes = df_quotes.sort_values('Net % Change', ascending=False).reset_index(drop=True)

    df_quotes['Net % Change'] = ["{:.2f}".format(a) for a in df_quotes['Net % Change']]
    
    return df_quotes

# Get prices for Radar charts
def get_radar_prices(chart_days, candle_minutes, volatile_symbols):
    TDSession = TDClient(
        client_id=client_id,
        redirect_uri='http://localhost/test',
        credentials_path='td_state.json')

    TDSession.login()

    cur_day = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    price_end_date = str(int(round(cur_day.timestamp() * 1000)))
    price_start_date = str(int(round(datetime.datetime(cur_day.year, cur_day.month, cur_day.day).timestamp() * 1000)))
    
    sym = []
    da = []
    op = []
    cl = []
    hi = []
    lo = []

    for symbol in volatile_symbols:
        p_hist = TDSession.get_price_history(symbol, 
                                             period_type='day',
                                             frequency_type='minute', 
                                             frequency= str(candle_minutes),
                                             end_date = price_end_date,
                                             start_date = price_start_date)
                                             
        for candle in p_hist['candles']:
            sym.append(symbol)
            da.append(datetime.datetime.fromtimestamp(candle['datetime'] / 1000))
            op.append(candle['open'])
            cl.append(candle['close'])
            hi.append(candle['high'])
            lo.append(candle['low'])

    df_p_hist = pd.DataFrame({'Symbol': sym, 'Date': da, 'Open': op,
                              'Close': cl, 'High': hi, 'Low': lo})
    
    return df_p_hist

# Fetch tweets
def fetch_tweets(symbols):
    api = twitter.Api(consumer_key=twitter_config.twttr_ck,
                      consumer_secret=twitter_config.twttr_cs,
                      access_token_key=twitter_config.twttr_atk,
                      access_token_secret=twitter_config.twttr_ats)

    tweet_list = []

    for symbol in symbols:
        tweet_list.append(api.GetSearch(term=symbol, lang='en'))

    created = []
    user = []
    twt = []

    for tag in tweet_list:
        for tweet in tag:
            user.append(tweet.AsDict()['user']['name'])
            created.append(
                str(tweet.AsDict()['created_at'].split(' ')[1] + ' ' + tweet.AsDict()['created_at'].split(' ')[2] +
                    ' ' + tweet.AsDict()['created_at'].split(' ')[5] + ' ' + tweet.AsDict()['created_at'].split(' ')[
                        3]))
            twt.append(tweet.AsDict()['text'])

    df = pd.DataFrame({'Date': pd.to_datetime(created), 'User': user, 'Tweet': twt})

    df['Date'] = [time - datetime.timedelta(hours=5) for time in df['Date']]
    df = df.sort_values('Date', ascending=False).reset_index(drop=True)

    return df