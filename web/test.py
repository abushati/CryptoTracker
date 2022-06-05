from bson import ObjectId
from flask import Flask,  request, jsonify

from alerts.alerts import AlertCreationError, PercentChangeAlert, PriceAlert
from user.watchlist import WatchList
from utils.db import alerts_collection, alert_generate_collection, coin_info_collection
from coin.coinpair import CoinPair,InvalidCoinPair
from flask_cors import CORS, cross_origin


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


    coin_pairs_ids = [str(x['_id']) for x in res]
    for coinpair_id in coin_pairs_ids:
        print(coinpair_id)
        # Todo: check why it fails and which coin it fails for
        try:
            pair_info = get_coinpair_info_by_id(coinpair_id)
            coinpairs_info.append(pair_info)
        except:
            continue
    return {'coinpairs': coinpairs_info}