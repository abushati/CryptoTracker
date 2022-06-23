from coin.coinpair import load_all_coins
import time
from coin.api import CBClient


class ApiUpdater:
    UPDATE_QUEUE = 'update'
    UPDATE_KEY = 'update_interval'
    
    def __init__(self):
        self.cache = redis()
        self.all_coins = load_all_coins()
        self.api_client = CBClient()

    def fetch_coin_info(coinpair)
        res = self.api_client.get_coin_info(coinpair.coinpair_id)
        print(res)

    def queue_update(self, date):
        pass

    def coins_to_update(self):

        pass

    def _run(self):
        coins_to_update = self.coins_to_update()
        for coin in coins_to_update:
            coin_info = self.fetch_coin_info(coin)

    def run(self)
        while True:
            self._run()
            time.sleep(10)