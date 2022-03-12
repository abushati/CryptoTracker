import time
from datetime import datetime
import uuid

from utils.db import db

class WatchList:
    def __init__(self, user_id, watchlist_id=None):
        self.id = watchlist_id
        self.db = db
        self.user_id = user_id

        self.prepare()
        self.ENTITY_MAPPING = {
            'alert': self.alerts,
            'coin': self.watchlist_coins
        }

    def prepare(self):
        user_watchlist = db['user_info'].find_one({'user_id':self.user_id})

        if not user_watchlist:
            print('Creating new watchlist for user')
            self.create_new()
            return

        self.load_watchlist()

    def create_new(self):
        db['user_info'].insert_one({'user_id':self.user_id,'watchlist_id':str(uuid.uuid1())})
        self.prepare()

    def load_watchlist(self):
        res = db['user_info'].find_one({'user_id':self.user_id})

        watchlist_coins = res.get('watched_coins') or []
        self.alerts = res.get('alerts') or []
        self.watchlist_id = res['watchlist_id']

        self.watchlist_coins = []
        for coin_sym in watchlist_coins:
            self.watchlist_coins.append(coin_sym)

        watchlist_alerts = res.get('alerts') or []
        self.alerts = []
        for alert_id in watchlist_alerts:
            self.alerts.append(alert_id)

    def add_coin(self,coin_id):
        coin_ids = [x for x in self.watchlist_coins]
        if coin_id not in coin_ids:
            self.watchlist_coins.append(coin_id)
        else:
            print(f'Coin {coin_id} already in watchlist')

    def add_alert(self,alert_id):
        alert_ids = [x for x in self.alerts]
        if alert_id not in alert_ids:
            self.watchlist_coins.append(alert_id)
        else:
            print(f'Alert {alert_id} already in watchlist')

    def add_to_watchlist(self,entity_type,entity_id):
        list_of_entities = self.ENTITY_MAPPING[entity_type]
        ids = [x for x in list_of_entities]
        if entity_id not in ids:
            list_of_entities.append(entity_id)
        else:
            print(f"Can't add coin {entity_id} to watchlist")

    def remove_from_watchlist(self,entity_type,entity_id):
        list_of_entities = self.ENTITY_MAPPING[entity_type]
        ids = [x for x in list_of_entities]
        if entity_id in ids:
            self.watchlist_coins.remove(entity_id)
        else:
            print(f"Can't remove coin {entity_id} from watchlist")

    def perform_watch_list_coin_action(self, action, entity_type,id):
        VALID_ACTIONS = {'remove':self.remove_from_watchlist,'add':self.add_to_watchlist}
        VALID_ENTITY_TYPE = ['alert','coin']

        if action in VALID_ACTIONS and entity_type in VALID_ENTITY_TYPE:
            action_fuc = VALID_ACTIONS[action]
            action_fuc(entity_type, id)
        self.save_changes()

    def save_changes(self):
        update_query = {'$set':{'watched_coins':[x for x in self.watchlist_coins],'alerts':[x for x in self.alerts]}}
        db['user_info'].update_one({'user_id':self.user_id,'watchlist_id':self.watchlist_id},update_query)


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
                alert.run_check()
            else:
                print(f'skipping alert {alert}')
        else:
            print(f'No alerts set on watchlist {self.wl.id}')

    def run(self):
        while True:
            if self.check_ready():
                self.check_alerts()
            time.sleep(1)

user_watchlist = WatchList(user_id='1')
user_watchlist.perform_watch_list_coin_action('add','alert','iasdfjkadsjf3')