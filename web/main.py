from bson import ObjectId
from flask import Flask,  request, jsonify

from alerts.alerts import AlertCreationError, PercentChangeAlert, PriceAlert
from user.watchlist import WatchList
from utils.db import alerts_collection, alert_generate_collection, coin_info_collection
from coin.coinpair import CoinPair,InvalidCoinPair
from flask_cors import CORS, cross_origin

def jsonify(d: dict):
    for key, value in d.items():
        if isinstance(value, ObjectId):
            d[key]=str(value)
    return d

app = Flask(__name__)
CORS(app)
@app.errorhandler(500)
@cross_origin()
@app.route('/watchlist/<action>',methods=['POST'])
def watchlist_action(action):
    valid_watchlist_actions = ['add','remove']
    if action not in valid_watchlist_actions:
        return f'Invalid action {action}', 400

    body = request.get_json(force=True)
    user_id = body.get('user_id')
    entity_type = body.get('entity_type')
    entity_id = body.get('entity_id')
    user_watchlist = WatchList(user_id)
    user_watchlist.perform_watch_list_coin_action(action, entity_type, entity_id)

    return 'success', 200

@app.errorhandler(500)
@cross_origin()
@app.route('/watchlist',methods=['GET'])
def user_watchlist():
    user_id = '1'
    user_watchlist = WatchList(user_id)
    user_coinpairs = user_watchlist.watchlist_coins
    user_alerts = user_watchlist.alerts

    c_info = []
    a_info = []
    for c_id in user_coinpairs:
        c_info.append(get_coinpair_info_by_id(c_id))

    for a_id in user_alerts:
        a_info.append((get_alert_by_id(a_id)))
    return {
        'coinpairs':c_info,
        'alerts':a_info
    }

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

def get_coinpair_info_by_id(coinpair_id, include_history=False):
    try:
        coinpair = CoinPair.get_by_id(coinpair_id)
    except InvalidCoinPair:
        return None
    return {
        'coinpair_id': coinpair_id,
        'coinpair_sym': coinpair.coin_pair_sym,
        'coinpair_price': coinpair.price(include_time=True),
        'coinpair_history': coinpair.pair_history('price',span='hours') if include_history else {}
    }

@app.route('/coinpair/<coinpair_id>', methods=['GET'])
@cross_origin()
def coinpair(coinpair_id=None):
    if not coinpair_id:
        return 'No coinpair_id provided', 400

    coin_info = get_coinpair_info_by_id(coinpair_id, include_history=True)
    if not coin_info:
        return 'Invalid coinpair_id provided', 400
    return coin_info
#Todo: this function takes too long, have to work on caching the price_history in coinpair
@app.route('/coinpairs', methods=['GET'])
@cross_origin()
def coinpairs():
    offset = request.args.get('offset', default = 0, type = int)

    coinpairs_info = []
    limit_size = 20
    skip_size  = limit_size * offset

    res = coin_info_collection.find({}, {'_id': 1}) \
        .sort('coin_pair', 1) \
        .skip(skip_size) \
        .limit(limit_size)
    
    coin_pairs_ids = [str(x['_id']) for x in res]
    for coinpair_id in coin_pairs_ids:
        print(coinpair_id)
        #Todo: check why it fails and which coin it fails for
        try:
            pair_info = get_coinpair_info_by_id(coinpair_id)
            coinpairs_info.append(pair_info)
        except:
            continue
    return {'coinpairs':coinpairs_info}



@app.errorhandler(500)
@app.route('/alert/<alert_id>', methods=['GET','PUT','DELETE'])
@cross_origin()
def alert(alert_id:None):    
    try:
        alert_id = ObjectId(alert_id)
    except:
        return 'Invalid alert id'

    if request.method == 'GET':
        alert  = alerts_collection.find_one({'_id':alert_id})
        if not alert:
            return 'No alert with that alert id found'
        return jsonify(alert)
    elif request.method == 'PUT':
        updated_alert = request.get_json(force=True, silent=True)
        clean_alert = dict(updated_alert)
        if not updated_alert:
            return 'Failed to get update alert json'
        
        valid_fields = ['alert_type','long_running','notification_settings','threshold','threshold_condition']
        keys = clean_alert.keys()
        to_pop = set(keys) - set(valid_fields)
        for pop in to_pop:
            clean_alert.pop(pop)

        alerts_collection.find_one_and_update({'_id':alert_id},{'$set':clean_alert})
        return 'Alert updated'
    elif request.method == 'DELETE':
        result = alerts_collection.delete_one({'_id':alert_id})
        if result.deleted_count == 1:
            return 'alert successfully deleted'
        elif result.deleted_count == 0:
            return 'Failed to delete alert '


@app.errorhandler(500)
@app.route('/alerts', methods=['GET','POST'])
@cross_origin()
def alerts():
    if request.method == 'POST':
        try:
            raw_alert = request.get_json(force=True)
            alert_type = raw_alert.get('alert_type')
            coin_sym = raw_alert.get('coin_sym')
            threshold = raw_alert.get('threshold')
            #Todo: need to check if notification method and value are cleaned
            notification_method = raw_alert.get('notification_settings_method')
            notification_value = raw_alert.get('notification_settings_value')
            print(notification_method,notification_value)
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
            #Todo: actually save the alert lmfaooooo

            alert_data = dict(coin_pair_id=coin.pair_id,
                        threshold=threshold,
                        tracker_type=tracker_type,
                        threshold_condition=threshold_condition,
                        notification_settings={
                            'method': notification_method,
                            'destination_val': notification_value}
                            )
            alert_types = {
                'percent':PercentChangeAlert,
                'price':PriceAlert
            }
            alert = alert_types.get(alert_type)
            try:
                alert.create_new(alert_data)
            except AlertCreationError:
                return 'Alert creation error', 400

        except:
            import sys
            import traceback
            print("500 error caught")
            etype, value, tb = sys.exc_info()
            print(traceback.print_exception(etype, value, tb))
        return {'success': True}
    elif request.method == 'GET':
    
        def clean_alert(d):
            for key, value in d.items():
                if isinstance(value, ObjectId):
                    d[key]=str(value)
            return d

        #Todo: have to overwrite the find method to do this
        all_alerts = [alert for alert in alerts_collection.find({})]
        alert_ids = [{'alert_id':alert.get('_id')} for alert in all_alerts]
        
        generated_alerts = {}
        for generated_alert in alert_generate_collection.find({'$or' : alert_ids }):
            alert_id = generated_alert.get('alert_id')
            if alert_id in generated_alerts:
                generated_alert = clean_alert(generated_alert)
                generated_alerts[alert_id].append(generated_alert)
            else:
                generated_alert = clean_alert(generated_alert)
                generated_alerts[alert_id] = [generated_alert]

        alerts = []
        for alert in all_alerts:
            al = {
                'alert_id':str(alert.get('_id')),
                'alert_type':alert.get('alert_type'),
                'coin_pair_id': str(alert.get('coin_pair_id')),
                'insert_time': alert.get('insert_time'),
                'long_running': alert.get('long_running'),
                'threshold': alert.get('threshold'),
                'threshold_condition': alert.get('threshold_condition'),
                'generation_history':generated_alerts.get(alert.get('_id'),[])
            }
            alerts.append(al)

        return {'alerts':alerts}

def start():
    app.run(host="0.0.0.0",port=5001, debug=True)
