from coin_updater import CoinHistoryUpdater
from websocket_reader import RealtimeFeedReader
import multiprocessing

def run():
    updater = CoinHistoryUpdater()
    multiprocessing.Process(target=updater.run)
    reader = RealtimeFeedReader()
    multiprocessing.Process(target=reader.run)



