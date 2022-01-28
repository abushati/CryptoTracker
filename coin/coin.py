import time

from .api import CBClient
from utils.db import db, desc_sort

from dataclasses import dataclass
from datetime import datetime
from utils.redis import redis
from datetime import datetime
import time


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
# @dataclass
# class Coin:
#     coin_id: str
#     coin_name: str
#     price_history: list(CoinPrice)

class Coin:
    def __init__(self, coin_id):
        self.coindb = db
        self.api_client = CBClient()
        self.cache = redis()

        self.coin_sym = coin_id
        self._load_coin()

    def get_current_stats(self):
        self.price()
        self.current_volumne()

    def current_volumne(self):
        pass

    def current_price(self):
        return self.price()[0]

    def price(self, cached=False):
        cache_key = f'current_price:{self.coin_sym}'
        cached_price = self.cache.get(cache_key)

        if not cached or not cached_price:
            print('Fetching current price from API')
            price = float(self.api_client.get_coin_current_price(self.coin_sym))
            insert_time = datetime.now()
            cache_value = f'{price}||{insert_time}'
            # Expire after 15 mins
            self.cache.set(cache_key, cache_value, ex=900)
            print(f'Saving in cache, {cache_key}={cache_value}')

            return price,None
        elif cached:
            print('Found in cache')
            price, insert_time = cached_price.decode("utf-8").split('||')

            return price,insert_time

    def _load_coin(self):
        coin_document = self.coindb['coin_info'].find_one({'coin_sym':self.coin_sym})
        if not coin_document:
            print('No document found for coin symbol named {}, creating'.format(self.coin_sym))
            self.create_new()
            return

        self.coin_name = coin_document['coin_name']
        self.coin_id = coin_document.get('_id')
        coin_history = self.coindb['coin_history'].find({'coin_id':self.coin_id}).sort('time', direction=desc_sort)

        self.price_history = []
        for history in coin_history:
            self.price_history.append(CoinPrice(price=history['price'],insert_time=history['time']))

    def create_new(self):
        #Todo: check if coin is valid, via CB api
        self.coindb['coin_info'].insert_one({
            'coin_sym':self.coin_sym,
            'coin_name':'temp'
        })
        return Coin(self.coin_sym)

    def update_coin(self):
        self.get_current_stats()


class CoinHistoryUpdater:

    def __init__(self):
        from utils.db import coin_history_collection, coin_info_collection

        self.history_col = coin_history_collection
        self.coin_col = coin_info_collection
        self.run_interval = 60

    def get_current_values(self,coin: Coin):
        info = {'price':None,'volume':None}
        price = coin.current_price()
        info['price'] = price

        return info

    def update_history_col(self,coin,history_type,new_info):
        col_field = history_type

        update_query = {'coin_id': coin.coin_id, 'time': datetime.utcnow(), 'type': history_type, col_field: new_info}
        self.history_col.insert_one(update_query)

    def run(self):
        coins = self.load_all_coins()
        last_run = datetime.now()

        while True:
            for coin in coins:
                current_values = self.get_current_values(coin)

                for key, current_value in current_values.items():
                    if current_value:
                        self.update_history_col(coin,key,current_value)

            print(f'sleeping for {self.run_interval}')
            time.sleep(self.run_interval)


    def load_all_coins(self):
        res = self.coin_col.find({},{'coin_sym':1})
        return [Coin(coin['coin_sym']) for coin in res]

