
import time
from pprint import pprint
from coin import Coin
class CoinUpdater():
    def __init__(self):
        # Todo : this updater shouldn't have anything to do with a watchlist
        coin = Coin('ADA-USD')
        while True:
            coin.update_coin()
            pprint(f'Coin update {coin.coin_id}')
            time.sleep(15)

if __name__ == '__main__':
    CoinUpdater()