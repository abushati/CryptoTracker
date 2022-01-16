from api import CBClient
import json
from cached_property import cached_property_with_ttl, cached_property
from dataclasses import dataclass
from datetime import datetime
from redis import Redis
from timeit import default_timer as timer
import pymongo

@dataclass
class CoinPrice:
    price: float
    insert_time: type(datetime)

# @dataclass
# class Coin:
#     coin_id: str
#     coin_name: str
#     price_history: list(CoinPrice)

class Coin:
    def __init__(self, coin_id):
        self.coin_sym = coin_id
        self.coindb = pymongo.MongoClient("mongodb+srv://tracker:admin@cluster0.szrgk.mongodb.net/test")['coinInfo']
        self.coin_attrs = ['coin_sym', 'coin_name', 'price_history']
        self._load_coin()
        self.api_client = CBClient()
        self.cache = Redis(host='127.0.0.1', port=6379)

    def get_current_stats(self):
        self.current_price()
        self.current_volumne()

    def current_volumne(self):
        pass

    def current_price(self, force=False):
        cache_key = f'current_price:{self.coin_sym}'
        cached_price = self.cache.get(cache_key)

        if force or not cached_price:
            print('Fetching current price from API')
            price = float(self.api_client.get_coin_current_price(self.coin_sym))
            insert_time = datetime.now()
            cache_value = f'{price}||{insert_time}'
            # Expire after 15 mins
            self.cache.set(cache_key, cache_value, ex=900000)
            print('saving in cache')
            # Only add to history if a force or cache expires
            self.price_history.append(price)
            self.coindb['coin_history'].insert_one({'coin_id':self.coin_id,'price':price,'time':insert_time})
            price = CoinPrice(price=price, insert_time=insert_time)
            return price
        else:
            print('Found in cache')
            price, insert_time = cached_price.decode("utf-8") .split('||')
            price = CoinPrice(price=float(price), insert_time=insert_time)
            return price

    def _load_coin(self):
        coin_document = self.coindb['coin_info'].find_one({'coin_sym':self.coin_sym})
        if not coin_document:
            print('No collection found coin symbol named {}, creating'.format(self.coin_sym))
            self.create_new()
            return

        self.coin_name = coin_document['coin_name']
        self.coin_id = coin_document.get('_id')

        coin_history = self.coindb['coin_history'].find({'coin_id':self.coin_id}).sort('time',direction=pymongo.DESCENDING)

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

    def update_attr(self, attr, value):
        if attr not in self.coin_attrs:
            print('attr {attr} not supported')
            return
        setattr(self, attr, value)
        #self._save_coin()


    def update_coin(self):
        self.get_current_stats()






