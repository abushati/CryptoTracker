from werkzeug.utils import cached_property

from .api import CBClient
from utils.db import db, desc_sort, coin_info_collection,coin_history_collection
from bson.objectid import ObjectId
from dataclasses import dataclass
from utils.redis_handler import redis
from datetime import datetime, timedelta

class InvalidCoinPair(Exception):
    pass

@dataclass
class CoinPrice:
    price: float
    insert_time: type(datetime)
    # https://stackoverflow.com/questions/27522626/hash-function-in-python-3-3-returns-different-results-between-sessions
    '''Note: By default, the __hash__() values of str, bytes and datetime objects are “salted” with an unpredictable random value. Although they remain constant within an individual Python process, they are not predictable between repeated invocations of Python.
    This is intended to provide protection against a denial-of-service caused by carefully-chosen inputs that exploit the worst case performance of a dict insertion, O(n^2) complexity. See http://www.ocert.org/advisories/ocert-2011-003.html for details.
    Changing hash values affects the iteration order of dicts, sets and other mappings. Python has never made guarantees about this ordering (and it typically varies between 32-bit and 64-bit builds).
    See also PYTHONHASHSEED.'''
    def __hash__(self):
        # hash(custom_object)
        return hash((self.price, self.insert_time))

    @property
    def hash(self):
        return str(self.price)+str(self.insert_time)

class CoinPair:
    def __init__(self, coin_pair_id):
        self.coindb = db
        self.api_client = CBClient()
        self.cache = redis()

        #Todo: have to catch this error bson.errors.InvalidId: '61f5814d32e2534f6e8e0eb34' is not a valid ObjectId,
        # it must be a 12-byte input or a 24-character hex string

        self.pair_id = ObjectId(coin_pair_id)
        self._load_pair()

    def _load_pair(self):
        coin_document = self.coindb['coin_info'].find_one({'_id':self.pair_id})
        if not coin_document:
            print('No document found for coin pair id {}'.format(self.pair_id))
            raise InvalidCoinPair

        self.coin_name = coin_document['coin_name']
        self.coin_pair_sym = coin_document.get('coin_pair')

    def current_volumne(self):
        pass

    def price(self, from_cache=True, include_time=False):
        cache_key = f'current_price:{self.pair_id}'
        cached_price = self.cache.get(cache_key)
        if from_cache and cached_price:
            print('Found in cache')
            price, insert_time = cached_price.decode("utf-8").split('||')
        else:
            print(f'Fetching current price from DB for pair {self.coin_pair_sym}')
            coinprice = self.pair_history('price',most_recent=True).get('hour_values')[0]
            price, insert_time = coinprice.price, coinprice.insert_time
            cache_value = f'{price}||{insert_time}'
            # Expire after 15 mins
            self.cache.set(cache_key, cache_value, ex=900)
            print(f'Saving in cache, {cache_key}={cache_value}')

        if include_time:
            return {'price':price, 'time':insert_time}
        else:
            return {'price':price}

    def _get_pair_history(self, history_type, start_time, include_addition_info=False):
        #Todo: This will only fetch the document that has a creation time greater than start_time. but the one previous
        # document will have price values that are still greater than start_time but filter won't match

        res = coin_history_collection.find(filter={'coin_id': self.pair_id, 'type': history_type, 'time':{'$gte':str(start_time)}}
                                           ).sort('time', direction=desc_sort)
        pair_history = []
        for r in res:
            hour_values = r.get(history_type)
            hour_min = r.get('min_value')
            hour_max = r.get('max_value')
            hour_average = r.get('average')

            # have to reverse as the newest history_type are pushed to the end of the array by CoinHistoryUpdater
            values = []
            for price in reversed(hour_values):
                values.append(CoinPrice(price.get('price'), price.get('time')))

            pair_history.append({
                'hour_min':hour_min,
                'hour_max':hour_max,
                'hour_average':hour_average,
                'hour_values':values
            })

        return pair_history

    #Todo: save this to redis,need to think how we would cache these.
    def pair_history(self, history_type, span='days', amount=1, most_recent=False):
        def _start_date(span,amount):
            start_time = datetime.utcnow()
            delta = timedelta(**{span: amount})
            return start_time - delta

        valid_time_spans = ('days', 'minutes', 'hours', 'weeks')
        # Todo: would have to put some limit of this or we would go to -infinite.
        #   What happens if there is no pair history? Perhaps check first
        pair_has_history = bool(coin_history_collection.find(filter={'coin_id': self.pair_id, 'type': history_type}))
        if not pair_has_history:
            print(f'This coin pair {self} has no history')
            return

        #Most recent doesn't always mean that the most recent value we have was an hour ago.
        #What if updater was down
        if most_recent:
            span = 'hours'
            amount = 1
        elif span not in valid_time_spans or not isinstance(amount,int):
            print(f'span {span} in invalid or amount is not an int')
            return

        start_time = _start_date(span,amount)
        pair_history = self._get_pair_history(history_type, start_time)
        if most_recent:
            return pair_history[0]

        return pair_history

    @staticmethod
    def get_coinpair_by_sym(sym):
        print(sym.upper())
        res = coin_info_collection.find_one({'coin_pair':sym.upper()},{'_id':1})
        print(res)
        if not res:
            raise InvalidCoinPair

        return CoinPair(res['_id'])



class CoinInit:

    def __init__(self):
        self.api = CBClient()
        self.coin_col = coin_info_collection

    def run_sync(self):
        print('syncing coins')
        all_saved = self.coin_col.find()
        saved_pairs = [x['coin_pair'] for x in all_saved]
        coins_pairs = self.api.get_all_currency_pairs()
        coins = self.api.get_all_currencies()
        d = {coin.get('id'): coin for coin in coins}

        to_insert = []
        for pair in coins_pairs:
            pair_id = pair.get('id')
            if pair_id not in saved_pairs:
                to_insert.append(pair_id)

        if to_insert:
            print(f'Coins to insert {to_insert}')
            self.coin_col.insert_many([{'coin_pair': pair,
                                        'coin_name':d.get(pair.split('-')[0]).get('name')} for pair in to_insert])
        else:
            print('No new coins to insert')

    def reset_coin_col(self):
        # Todo: there are other collections that use the object id of the coin, so we have to at least return the object
        #  id and either save the new coin-pairs to the same id or clear all references to that coin-pair
        self.coin_col.delete_many({})
        self.run_sync()




