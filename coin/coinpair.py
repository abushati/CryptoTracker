# from anyio import current_effective_deadline
from werkzeug.utils import cached_property

# from .api import CBClient
from utils.db import db, desc_sort, coin_info_collection,coin_history_collection, coinpair_ticker_data
from bson.objectid import ObjectId
from bson.errors import InvalidId
from dataclasses import dataclass
from utils.redis_handler import redis
from datetime import datetime, timedelta, timezone

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
    coindb = db
    coin_col = coin_info_collection
    
    def __init__(self, coin_pair_id):
        
        # self.api_client = CBClient()
        if isinstance(coin_pair_id, str):
            coin_pair_id = ObjectId(coin_pair_id)

        self.pair_id = coin_pair_id
        self.cache = redis()
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
            coinprice = CoinPrice(price,insert_time)
        else:
            print(f'Fetching current price from DB for pair {self.coin_pair_sym}')
            coinprice = self._price()
            price, insert_time = coinprice.price, coinprice.insert_time
            cache_value = f'{price}||{insert_time}'
            # Expire after 15 minsx
            self.cache.set(cache_key, cache_value, ex=30)
            print(f'Saving in cache, {cache_key}={cache_value}')

        if include_time:
            return coinprice
        else:
            return coinprice.price

    def _price(self):
        res = coinpair_ticker_data.find({'product_id':self.coin_pair_sym}).sort('time',direction=desc_sort)
        most_recent_data = [data for data in res][0]
        current_price = most_recent_data.get('price')
        current_price_time = most_recent_data.get('time')
        coinpair_price = CoinPrice(price=current_price,insert_time=current_price_time)
        # most_recent_data = self.pair_history('price',most_recent=True)
        # current_price = most_recent_data.get('hour_values')[0]
        return coinpair_price

    def _get_pair_history(self, history_type, start_time, include_addition_info=False):
        product_filter = {'product_id': self.coin_pair_sym, 
                            'time': {
                            '$gt': start_time
                            }
                        }
        agra_query = [
            {
                '$match': product_filter
            }, {
                '$group': {
                    '_id': '$product_id', 
                    'avg': {'$avg': '$price'},
                    'min': {'$min': '$price'},
                    'max': {'$max': '$price'}
                }
            }
        ]
        meta_data = [r for r in coinpair_ticker_data.aggregate(agra_query)]
        if meta_data:
            meta_data = meta_data[0] 
        else:
            meta_data = {}
        price_values = coinpair_ticker_data.find(filter=product_filter).sort('time',direction=desc_sort)

        values = []
        for price in price_values:
            values.append(CoinPrice(price.get('price'), price.get('time')))

        if not meta_data and not values:
            return None

        pair_history = {
            'hour_min':meta_data.get('min'),
            'hour_max':meta_data.get('max'),
            'hour_average':meta_data.get('avg'),
            'hour_values':values
        }
        print(pair_history)
        return pair_history

    #Todo: save this to redis,need to think how we would cache these.
    def pair_history(self, history_type, span='days', amount=1, most_recent=False):
        def _start_date(span,amount):
            start_time = datetime.utcnow()
            delta = timedelta(**{span: amount})
            return start_time - delta

        valid_time_spans = ('days', 'minutes', 'hours', 'weeks')
        if most_recent:
            span = 'hours'
            amount = 1
        elif span not in valid_time_spans or not isinstance(amount,int):
            print(f'span {span} in invalid or amount is not an int')
            return

        start_time = _start_date(span,amount)
        pair_history = self._get_pair_history(history_type, start_time)

        return pair_history

    @classmethod
    def get_by_id(cls,coinpair_id):
        try: 
            pair_id = ObjectId(coinpair_id)
        except InvalidId:
            print(f'Invalide coinpair_id provided: {coinpair_id}')
            return None
        return cls(pair_id)

    @staticmethod
    def get_coinpair_by_sym(sym):
        res = coin_info_collection.find_one({'coin_pair':sym.upper()},{'_id':1})
        print(res)
        if not res:
            raise InvalidCoinPair

        return CoinPair(res['_id'])

    @classmethod
    def load_all_coins(cls):
        # The source of where we get the data donesn't effect the speed in returning the data. have to look into the
        # initializing of each coin pair
        res = cls.coin_col.find({},{'_id':1})
        coin_pairs_ids = [str(x['_id']) for x in res]
        # yield [CoinPair(pair) for pair in coin_pairs_ids]
        coinpairs = []
        for c_id in coin_pairs_ids:
            try:
                c = CoinPair(c_id)
                yield c
            except InvalidCoinPair:
                continue
        # return coinpairs


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



