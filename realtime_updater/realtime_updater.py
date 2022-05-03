from realtime_updater.coin_updater import CoinHistoryUpdater
from realtime_updater.websocket_reader import RealtimeFeedReader
import multiprocessing

def run():
    updater = CoinHistoryUpdater()
    p1 = multiprocessing.Process(updater.run)
    p1.start()

    reader = RealtimeFeedReader()
    p2 = multiprocessing.Process(reader.run)
    p2.start()


# updater = CoinHistoryUpdater()
# updater.run()