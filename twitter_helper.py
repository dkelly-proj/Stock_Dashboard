import tweepy
import twitter_config
import datetime
import pandas as pd

# Fetch tweets
def fetch_tweets(symbols):
    # Authorization
    auth = tweepy.OAuthHandler(twitter_config.twttr_ck, twitter_config.twttr_cs)
    auth.set_access_token(twitter_config.twttr_atk, twitter_config.twttr_ats)
    api = tweepy.API(auth)

    # Search for tweets on symbols
    tweets = api.search(' OR '.join(['$' + symbol for symbol in symbols]),
                        tweet_mode='extended', count=20, lang='en')

    record = []

    for tweet in tweets:
        record.append(["Twitter", tweet.author.screen_name, tweet.full_text])

    df = pd.DataFrame(record, columns=['Source', 'User', 'Tweet'])

    df = df[~df['Tweet'].str.startswith('RT')].reset_index(drop=True)

    return df