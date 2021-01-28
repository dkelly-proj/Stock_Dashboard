import twitter
import twitter_config
import datetime
import pandas as pd

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