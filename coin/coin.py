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
    insert_time: str

class Coin:
    def __init__(self, coin_id):
        self.coin_id = coin_id
        self.coindb = pymongo.MongoClient("mongodb+srv://tracker:admin@cluster0.szrgk.mongodb.net/test")['coinInfo']

        self.coin_attrs = ['coin_id', 'coin_name', 'price_history', 'lowest_price', 'highest_price']
        self._load_coin()
        self.api_client = CBClient()
        self.cache = Redis(host='127.0.0.1', port=6379)


    def current_price(self, force=False):
        cache_key = f'current_price:{self.coin_id}'
        cached_price = self.cache.get(cache_key)

        if force or not cached_price:
            print('Fetching current price from API')
            price = float(self.api_client.get_coin_current_price(self.coin_id))
            insert_time = str(datetime.now())
            cache_value = f'{price}||{insert_time}'
            # Expire after 15 mins
            self.cache.set(cache_key, cache_value, ex=900000)
            print('saving in cache')

            price = CoinPrice(price=price, insert_time=insert_time)
            self.price_history.append(price)
            return price
        else:
            print('Found in cache')
            price, insert_time = cached_price.decode("utf-8") .split('||')
            price = CoinPrice(price=float(price), insert_time=str(insert_time))
            return price

    def _load_coin(self):
        if self.coin_id not in self.coindb.list_collection_names():
            print('No collection found named {}, creating'.format(self.coin_id))
            self.coindb.create_collection(self.coin_id)
            return

        self.coin_name = ''
        self.price_history = []
        default_values ={
            'coin_name': '',
            'price_history':[],
        }

        with open('./coin_db.json', 'r') as coin_db:
            coin_db_coins = json.loads(coin_db.read()).get('tokens')
        #{{"tokens": [{"coin_id": "ADA-USD", "coin_name": "", "price_history": [{"price": 1.2574, "insert_time": "2022-01-13 23:29:52.978626"}]}]}
        for coin in coin_db_coins:
            if coin['coin_id'] == self.coin_id:
                for attr in self.coin_attrs:
                    try:
                        value = coin.get(attr)
                        if not value:
                            value = default_values.get(attr)

                        if attr == 'price_history':
                            value = [CoinPrice(price=float(price.get('price')),insert_time=price.get('insert_time')) for price in value]

                        setattr(self, attr, value)
                    except Exception as e:
                        print('skipping setting coin field, {}'.format(e))
                        continue

        coin_document = self.coindb[self.coin_id]

    def update_attr(self, attr, value):
        if attr not in self.coin_attrs:
            print('attr {attr} not supported')
            return
        setattr(self, attr, value)
        self._save_coin()

    def _save_coin(self):
        for attr in self.coin_attrs:
            v = self.__dict__.get(attr)
            if attr == 'price_history':
                l = [price_history.__dict__ for price_history in v]
                coin[attr] = l
            else:
                coin[attr] = v

        new_coin = True
        if new_coin:
            self.coindb.create_collection()


    def update_coin(self):
        self.current_price
        self._save_coin()





