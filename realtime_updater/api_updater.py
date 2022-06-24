from coin.coinpair import CoinPair
import time
from coin.api import CBClient
from utils.redis_handler import redis


class ApiUpdater:
    UPDATE_QUEUE = 'update'
    UPDATE_KEY = 'update_interval'
    
    def __init__(self):
        self.cache = redis()
        self.all_coins = CoinPair.load_all_coins()
        self.api_client = CBClient()

    def fetch_coin_info(self, coinpair):
        res = self.api_client.get_coin_info(coinpair.coin_pair_sym)
        print(res)

    def queue_update(self, date):
        pass

    def coins_to_update(self):
        to_update = []
        for coin in self.all_coins:
            coin_id = coin.pair_id
            print(f'to update via api coin id')
            if not int(self.cache.exists(f'{self.UPDATE_KEY}:{coin_id}')):
                print(f'to update via api coin id{coin_id}')
                # to_update.append(coin)
                yield coin
        # return to_update

    def _run(self):
        coins_to_update = self.coins_to_update()
        for coin in coins_to_update:
            coin_info = self.fetch_coin_info(coin)

    def run(self): 
        while True:
            self._run()
            time.sleep(10)

if __name__ == '__main__':
    a = ApiUpdater()
    a.run()