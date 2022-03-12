from bson import ObjectId
from flask import Flask,  request, jsonify
from watchlist import WatchList
from utils.db import alerts_collection, alert_generate_collection, coin_info_collection
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

def get_alert_by_id(alert_id):
    alert = alerts_collection.find_one({'_id':ObjectId(alert_id)})
    if not alert:
        return None

    return {
        'alert_type': alert.get('alert_type'),
        'coin_pair_id': str(alert.get('coin_pair_id')),
        'insert_time': alert.get('insert_time'),
        'long_running': alert.get('long_running'),
        'threshold': alert.get('threshold'),
        'threshold_condition': alert.get('threshold_condition')
    }

def get_coinpair_info(coinpair_id):
    try:
        coinpair = CoinPair(coinpair_id)
    except InvalidCoinPair:
        return None
    return {
        'coinpair_sym': coinpair.coin_pair_sym,
        'coinpair_price': coinpair.price(include_time=True),
        'coinpair_history': coinpair.pair_history('price',span='hours')
    }

#Todo: this function takes too long, have to work on caching the price_history in coinpair
@app.route('/coinpair/<coinpair_id>', methods=['GET'])
def coinpair(coinpair_id=None):
    if not coinpair_id:
        return 'No coinpair_id provided', 400

    coin_info = get_coinpair_info(coinpair_id)
    if not coin_info:
        return 'Invalid coinpair_id provided', 400
    return coin_info

@app.route('/coinpairs', methods=['GET'])
def coinpairs():
    coinpairs_info = []
    coin_col = coin_info_collection
    res = coin_col.find({}, {'_id': 1})
    coin_pairs_ids = [str(x['_id']) for x in res]
    for coinpair_id in coin_pairs_ids:
        print(coinpair_id)
        #Todo: check why it fails and which coin it fails for
        try:
            pair_info = get_coinpair_info(coinpair_id)
            coinpairs_info.append(pair_info)
        except:
            continue
    return {'coinpairs':coinpairs_info}

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

    elif request.method == 'GET':
        all_alerts = alerts_collection.find({})
        alerts = []
        for alert in all_alerts:
            al = {
                'alert_type':alert.get('alert_type'),
                'coin_pair_id': str(alert.get('coin_pair_id')),
                'insert_time': alert.get('insert_time'),
                'long_running': alert.get('long_running'),
                'threshold': alert.get('threshold'),
                'threshold_condition': alert.get('threshold_condition')
            }
            alerts.append(al)

        return {'alerts':alerts}

@app.route('/alerts_notification', methods=['GET'])
def alerts_generated():
    generated_alerts = alert_generate_collection.find({})
    output = []
    for gen_alert in generated_alerts:
        data = dict()
        alert_id = str(gen_alert.get('alert_id'))
        alert_info = get_alert_by_id(alert_id)
        data['alert']=alert_info
        #Todo: fix this, alert generation only saves the coin pair sym
        coinpair = CoinPair.get_coinpair_by_sym(gen_alert.get('coin_pair'))
        coin_info = {
            'coin_pair_sym':coinpair.coin_pair_sym,
            'coin_pair_price':coinpair.price(include_time=True)
        }
        data['coin_info']=coin_info
        msg = gen_alert.get('msg')
        data['msg'] = msg
        output.append(data)

    return {'alerts_generated':output}

def start():
    app.run(host="0.0.0.0", debug=True)
