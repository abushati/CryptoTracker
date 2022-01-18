
import time
from pprint import pprint
from coin import Coin,load_all_coins
import logging

'''
For logging 
Python output is buffered. Setting the environment variable PYTHONUNBUFFERED=1 in you supervisord.conf will disable buffering and show log messages sooner:
[program:x]
environment = PYTHONUNBUFFERED=1
or add the -u command-line switch to python command:

[program:x]
command = python -u file.py
'''


class CoinUpdater():
    def __init__(self):
        coins = load_all_coins()
        print(f'Coin updater running, valid coins {[x.coin_sym for x in coins]}')
        while True:
            for coin in coins:
                coin.update_coin()
                print(f'Coin update {coin.coin_sym}')
                # 300 == 5 mins
                time.sleep(300)

if __name__ == '__main__':
    CoinUpdater()