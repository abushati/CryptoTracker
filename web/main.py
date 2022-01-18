from flask import Flask
from watchlist import WatchList

app = Flask(__name__)
@app.route('/watchlist/add')
def add_to_watchlist():
    user_id = '1'
    coin = 'ADA-USD'
    # coin = 't'
    WatchList(user_id).perform_watch_list_coin_action('add',coin)
    return '<h1>Hello, World!</h1>'

@app.route('/watchlist/remove')
def remove_to_watchlist():
    user_id = '1'
    coin = 'ADA-USD'
    # coin = 't'
    WatchList(user_id).perform_watch_list_coin_action('remove',coin)
    return '<h1>Hello, World!</h1>'

def start():
    app.run(host="0.0.0.0", debug=True)
