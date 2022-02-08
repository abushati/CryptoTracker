# from web.main import start
# start()
import asyncio
import time

from coin.coin_updater import CoinHistoryUpdater
#temp
updater = CoinHistoryUpdater()
# asyncio.run(updater.run(fast=True))
# print(time.time() - s)
# print('Fast speed ^')
# time.sleep(2)
# asyncio.run(updater.run(fast=False))
# print('slow speed ^')
# # syncer = CoinSyncer()
updater.run()
