from flask import Flask,  request
from watchlist import WatchList
# from utils import db
from coin.coinpair import CoinPair,InvalidCoinPair

app = Flask(__name__)
@app.route('/watchlist/add')
def add_to_watchlist():
    ACTION: str = 'add'
    body = request.get_json()
    user_id = body.get('user_id')
    entity_type = body.get('entity_type')
    entity_id = body.get('entity_id')

    user_watchlist = WatchList(user_id)
    if entity_type == 'alert':
        alert = body.get('alert')
        # get the alert data from alert collection. to add the coin and the alert
        return '<h1>ADDED ALERT<h1>'

    elif entity_type == 'coin':
        user_watchlist.perform_watch_list_coin_action(ACTION, entity_type, entity_id)


    return '<h1>Hello, World!</h1>'

@app.route('/watchlist/remove')
def remove_to_watchlist():
    user_id = '1'
    coin_sym = 'ADA-USD'
    try:
        coin = CoinPair.get_coinpair_by_sym(coin_sym)
    except InvalidCoinPair:
        return 'Invalid coin pair symbol provide'

    WatchList(user_id).perform_watch_list_coin_action('remove',coin)
    return '<h1>Hello, World!</h1>'

def start():
    app.run(host="0.0.0.0", debug=True)
