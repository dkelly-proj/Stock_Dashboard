import pandas as pd
import praw


"""
#########################################
#           WEBSITE: https://medium.com/swlh/how-to-create-a-dashboard-to-dominate-the-stock-market-using-python-and-dash-c35a12108c93         #
#
using PRAW to connect to the Reddit API.
define the function get_reddit(). It takes in the API credentials and the subreddit name (wallstreetbets by default).
Notice within the function the data gets saved from Reddit to the variable posts. The data is then unpacked, 
and appended in list variable p, and then saved as pandas DataFrame object named posts_df.
#
######################################### 
"""

#return a dataframe for the newest reddit posts
def get_reddit(cid= 'Lgjng9yfw7Tgew', csec= 'E8ivymEjva1p6FmczIxgWKKrsOQVZg', uag= 'bbg-dashboard', subreddit='wallstreetbets'):
    reddit = praw.Reddit(client_id= cid, client_secret= csec, user_agent= uag)

    posts = reddit.subreddit(subreddit).new(limit=None)
    #hot_bets = reddit.subreddit('wallstreetbets').hot(limit=1000)

    p = []
    for post in posts:
        p.append([post.title, post.score, post.selftext])
    try:
        posts_df = pd.DataFrame(p,columns=['title', 'score', 'post'])
        # sorted_df = posts_df.sort_values(by='score', ascending=True)
        sorted_df = posts_df.nlargest(25, "score")
        print(sorted_df)
        return sorted_df
    except:
        print("your statement doesn't work")