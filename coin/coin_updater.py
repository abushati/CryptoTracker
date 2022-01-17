
import time
from pprint import pprint
from coin import Coin,load_all_coins
class CoinUpdater():
    def __init__(self):
        coins = load_all_coins()
        while True:
            for coin in coins:
                coin.update_coin()
                pprint(f'Coin update {coin.coin_sym}')
                # 300 == 5 mins
                time.sleep(300)

if __name__ == '__main__':
    CoinUpdater()