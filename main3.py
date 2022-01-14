from coin.coin_updater import CoinUpdater
from watchlist import WatchListCurrencyTracker

if __name__ == "__main__":
    CoinUpdater()

    wl_tracker = WatchListCurrencyTracker(wl)
    wl_tracker.run()