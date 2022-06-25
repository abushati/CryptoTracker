import datetime

from coin.coinpair import CoinPair
import time
from coin.api import CBClient
from utils.redis_handler import redis

# from realtime_updater.api_updater import ApiUpdater
# a = ApiUpdater()
# a.run()
import pickle

class ApiUpdater:
    UPDATE_QUEUE = 'update'
    UPDATE_KEY = 'update_interval'
    
    def __init__(self):
        self.cache = redis()
        self.all_coins = CoinPair.load_all_coins()
        self.api_client = CBClient()

    def fetch_coin_info(self, coinpair):
        mapping = {
            'open':'open_24h',
            'low':'low_24h',
            'high':'high_24h',
            'volume_30day':'volume_30d',
            'last': 'price'
        }
        re = {}
        res = self.api_client.get_coin_state(coinpair.coin_pair_sym)
        for key, value in res.items():
            if key in mapping:
                re[mapping[key]] = value

        re['time'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        re['product_id'] = coinpair.coin_pair_sym
        return re

    def queue_update(self, data):
        pickled_msg = pickle.dumps(data)
        print(f'queueing data {data}')
        self.cache.lpush('update', pickled_msg)

    def coins_to_update(self):
        for coin in self.all_coins:
            coin_id = coin.pair_id
            print(f'to update via api coin id')
            if not int(self.cache.exists(f'{self.UPDATE_KEY}:{coin_id}')):
                print(f'to update via api coin id{coin_id}')
                yield coin

    def _run(self):
        coins_to_update = self.coins_to_update()
        for coin in coins_to_update:
            coin_info = self.fetch_coin_info(coin)
            if not coin_info:
                print('Failed to get coin info, skipping')
                continue
            self.queue_update(coin_info)

    def run(self): 
        while True:
            self._run()
            time.sleep(10)

if __name__ == '__main__':
    a = ApiUpdater()
    a.run()