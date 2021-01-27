import pandas as pd
import praw


#return a dataframe for the newest reddit posts
def get_reddit(cid= 'Lgjng9yfw7Tgew', csec= 'E8ivymEjva1p6FmczIxgWKKrsOQVZg', uag= 'bbg-dashboard', subreddit='wallstreetbets'):
    reddit = praw.Reddit(client_id= cid, client_secret= csec, user_agent= uag)

    posts = reddit.subreddit(subreddit).new(limit=None)
    #hot_bets = reddit.subreddit('wallstreetbets').hot(limit=1000)

    p = []
    for post in posts:
        p.append([post.title, post.score, post.selftext])
    posts_df = pd.DataFrame(p,columns=['title', 'score', 'post'])
    return posts_df