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

@app.route('/alerts', methods=['GET','POST'])
def alerts():
    if request.method == 'POST':
        raw_alert = request.get_json()
        alert_type = raw_alert.get('alert_type')
        coin_sym = raw_alert.get('coin_sym')
        threshold = raw_alert.get('threshold')
        tracker_type = 'price'
        threshold_condition = raw_alert.get('threshold_condition')
        print(alert_type, threshold,threshold_condition, alert_type)

        if not coin_sym:
            return 'A coin symbol needs to be provided', 400
        elif not alert_type:
            return 'An alert type needs to be provided', 400
        elif not threshold:
            return 'A threshold needs to be provided', 400

        #Todo: check if long running is set, but also check if the alert type supports it

        try:
            coin = CoinPair.get_coinpair_by_sym(coin_sym)
        except InvalidCoinPair:
            return 'Invalid coin pair symbol provide'

        return coin.price(from_cache=False, include_time=True)
    return 'nice'

def start():
    app.run(host="0.0.0.0", debug=True)
