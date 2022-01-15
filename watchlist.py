import json
import time
from datetime import datetime

from coin.coin import Coin
from alerts import get_alerts

class WatchList:
    def __init__(self, watchlist_id):
        #List(Coins())
        self.watchlist_coins = self.load_watched_coins()
        self.alerts = get_alerts(watchlist_id) or []
        self.id = watchlist_id

    def load_watched_coins(self):
        #Todo: fetch data based on watchlist id
        with open('real_watchlist.json','r') as watchlist:
            import json
            coins = json.load(watchlist).get('tokens')

        if not coins:
            print('Nothing on token watchlist')
            return []

        list_of_coins = []
        for coin_id in coins:
            c = Coin(coin_id)
            list_of_coins.append(c)

        return list_of_coins

    def add_to_watchlist(self,coin_id):
        coin_ids = [x.coin_id for x in self.watchlist_coins]
        if coin_id not in coin_ids:
            self.watchlist_coins.append(Coin(coin_id))
        else:
            print(f'Coin {coin_id} already in watchlist')

    def remove_from_watchlist(self,coin_id):
        coin_ids = [x.coin_id for x in self.watchlist_coins]
        if coin_id in coin_ids:
            self.watchlist_coins.remove(Coin(coin_id))
        else:
            print(f"Can't remove coin {coin_id} from watchlist")

    def perform_watch_list_coin_action(self, action, coin):
        VALID_ACTIONS = {'remove':self.remove_from_watchlist,'add':self.add_to_watchlist}
        if action in VALID_ACTIONS:
            action_fuc = VALID_ACTIONS[action]
            action_fuc(coin.coin_id)
        self.save_changes()

    def save_changes(self):
        with open('real_watchlist.json', 'w') as watchlist:
            coin_ids = [x.coin_id for x in self.watchlist_coins]
            output = {'tokens': coin_ids}
            output_json = json.dumps(output)
            watchlist.write(output_json)


class WatchListCurrencyTracker:
    def __init__(self, watch_list):
        # Get watchlist 'd' is temp.py
        self.wl = watch_list
        # Have to get all the alerts per watchlist
        self.last_sync_check = datetime(2021, 1, 1, 0, 0, 0)
        self.watch_list_alerts = self.wl.alerts

    #Triggers
    def check_ready(self):
        now = datetime.now()
        delta = now - self.last_sync_check
        if delta.seconds >= 5:
            self.last_sync_check = now
            return True
        else:
            return False

    def check_alerts(self):
        for alert in self.watch_list_alerts:
            if alert.coin_specific and alert.coin in self.wl.watchlist_coins:
                alert.check()
            else:
                print(f'skipping alert {alert}')
        else:
            print(f'No alerts set on watchlist {self.wl.id}')

    def run(self):
        while True:
            if self.check_ready():
                self.check_alerts()
            time.sleep(1)

if __name__ == "__main__":
    wl = WatchListCurrencyTracker(WatchList(None))
    wl.run()