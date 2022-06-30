import datetime

from coin.coinpair import CoinPair
import time
from coin.api import CBClient
import pickle
from realtime_updater.coin_updater import UpdaterMixIn

class ApiUpdater(UpdaterMixIn):
    def __init__(self):
        self.api_client = CBClient()

    @property
    def all_coins(self):
        return CoinPair.load_all_coins()

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
        self.CACHE.lpush(self.UPDATE_QUEUE, pickled_msg)

    def coins_to_update(self):
        for coin in self.all_coins:
            if not self.update_key_exists(coin):
                print(f'Updating sym {coin.coin_pair_sym} via api')
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
            print('starting')
            self._run()
            print('sleeping')
            time.sleep(10)

if __name__ == '__main__':
    a = ApiUpdater()
    a.run()