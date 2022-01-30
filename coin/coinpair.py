import time

from .api import CBClient
from utils.db import db, desc_sort, coin_info_collection

from dataclasses import dataclass
from datetime import datetime
from utils.redis import redis
from datetime import datetime
import time

class FailedToFetchCoinPrice(Exception):
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
    def __init__(self, coin_id):
        self.coindb = db
        self.api_client = CBClient()
        self.cache = redis()

        self.coin_pair = coin_id
        self._load_coin()

    def current_volumne(self):
        pass

    def current_price(self, include_time=False):
        price = self.price()
        if include_time:
            return price
        else:
            return price[0]


    def price(self, cached=False):
        cache_key = f'current_price:{self.coin_pair}'
        cached_price = self.cache.get(cache_key)

        if not cached or not cached_price:
            print(f'Fetching current price from API for pair {self.coin_pair}')
            try:
                price = float(self.api_client.get_coin_current_price(self.coin_pair))
            except:
                raise FailedToFetchCoinPrice
            insert_time = datetime.utcnow()
            cache_value = f'{price}||{insert_time}'
            #Todo: from the updater history this function is called every minute so we are updating the cache every iteration

            # Expire after 15 mins
            self.cache.set(cache_key, cache_value, ex=900)
            print(f'Saving in cache, {cache_key}={cache_value}')

        elif cached:
            print('Found in cache')
            price, insert_time = cached_price.decode("utf-8").split('||')

        return {'price':price, 'time':insert_time}

    def _load_coin(self):
        coin_document = self.coindb['coin_info'].find_one({'coin_pair':self.coin_pair})
        if not coin_document:
            print('No document found for coin symbol named {}, creating'.format(self.coin_pair))
            return

        self.coin_name = coin_document['coin_name']
        self.coin_id = coin_document.get('_id')
        coin_history = self.coindb['coin_history'].find({'coin_id':self.coin_id})\
            .sort('time', direction=desc_sort).limit(30)

        self.price_history = []
        for history in coin_history:
            self.price_history.append(CoinPrice(price=history['price'],insert_time=history['time']))


class CoinHistoryUpdater:

    def __init__(self):
        from utils.db import coin_history_collection, coin_info_collection
        from utils.redis import redis

        self.cache = redis()
        self.history_col = coin_history_collection
        self.coin_col = coin_info_collection
        self.run_interval = 60

    def load_all_coins(self):
        # The source of where we get the data donesn't effect the speed in returning the data. have to look into the
        # initializing of each coin pair
        cache_key = 'coin_pairs'
        cached_pairs = self.cache.get(cache_key)
        if not cached_pairs:
            print('Fetching from db')
            res = self.coin_col.find({},{'coin_pair':1})
            coin_pairs = [x['coin_pair'] for x in res]
            self.cache.set(cache_key,','.join(coin_pairs))
            return [CoinPair(pair) for pair in coin_pairs]
        else:
            print('Fetching from cache')
            return [CoinPair(pair) for pair in cached_pairs.decode("utf-8").split(',')]

    def get_current_values(self, coin: CoinPair):
        info = {'price':None,'volume':None}
        info['price'] = coin.current_price(include_time=True)
        return info

    def update_history_col(self,coin,history_type,new_info):

        updatible_fields = {'average':lambda x:sum(x) / len(x),
                            'min_value':lambda x:min(x),
                            'max_value':lambda x: max(x)}

        col_field = history_type
        fetched_time = datetime.utcnow()
        insert_time_key = fetched_time.strftime('%Y-%m-%d %H:00:00')
        query = {'time': insert_time_key,
         'coin_id': coin.coin_id,
         'type': history_type}

        # return_fields = {x: 1 for x in updatible_fields}
        # return_fields[col_field] = 1

        res = self.history_col.find_one(query,{col_field:1})
        history_values = res.get(col_field) or []
        history_price_values = [x.get('price') for x in history_values]

        updates = {}
        if len(history_price_values) == 0:
            updates = {x: new_info for x in updatible_fields}
        else:
            for key, func in updatible_fields.items():
                updates[key] = func(history_price_values)

            self.history_col.find_one_and_update(query,
                                                 {'$push': {col_field: new_info},
                                                  '$set': updates},
                                                 upsert=True)

    def run(self):
        print('Loading coins for history update')
        s = time.time()
        coins = self.load_all_coins()
        print(time.time()-s)
        print('Done loading')
        last_run = datetime.now()

        while True:
            for coin in coins:
                try:
                    current_values = self.get_current_values(coin)
                except FailedToFetchCoinPrice as e:
                    print(f'Failed to get coin-pair current value, skipping {coin}, {e}')
                    continue

                for key, current_value in current_values.items():
                    if current_value:
                        self.update_history_col(coin,key,current_value)

            print(f'sleeping for {self.run_interval}')
            time.sleep(self.run_interval)

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




