# Stock Dashboard

## Files
### app.py
Main application that runs on Heroku

### local_app.py
Local version of the application for debugging. Basically the same as app.py with a couple of lines commented out that deal with Flask and servers.

### Procfile
File needed by Heroku

### runtime.txt
Specifying the version of Python used by Heroku

### td_helper.py
Helper functions for retrieving watchlist symbols, quotes, price history from TD Ameritrade. Also for retrieving Tweets from Twitter.
