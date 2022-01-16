
import time
from pprint import pprint
from coin import Coin
class CoinUpdater():
    def __init__(self):
        # Todo : this updater shouldn't have anything to do with a watchlist
        coin = Coin('ADA-USD')
        print(coin.price_history)
        while True:
            coin.update_coin()
            pprint(f'Coin update {coin.coin_id}')

            coin.current_price()
            time.sleep(2)

if __name__ == '__main__':
    CoinUpdater()