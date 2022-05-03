import time
from datetime import datetime
import uuid

from utils.db import db

class WatchList:
    def __init__(self, user_id):
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
        db['user_info'].insert_one({'user_id':self.user_id})
        self.prepare()

    def load_watchlist(self):
        res = db['user_info'].find_one({'user_id':self.user_id})

        watchlist_coins = res.get('watched_coins') or []
        self.alerts = res.get('alerts') or []

        self.watchlist_coins = []
        for coin_sym in watchlist_coins:
            self.watchlist_coins.append(coin_sym)

        watchlist_alerts = res.get('alerts') or []
        self.alerts = []
        for alert_id in watchlist_alerts:
            self.alerts.append(alert_id)

    def add_to_watchlist(self,entity_type,entity_id):
        list_of_entities = self.ENTITY_MAPPING[entity_type]
        ids = [x for x in list_of_entities]
        if entity_id not in ids:
            print('adding {entity_id} to watchlist')
            list_of_entities.append(entity_id)
        else:
            print(f"Can't add coin {entity_id} to watchlist. entity of type {entity_type} already in watchlist")
        print()

    def remove_from_watchlist(self,entity_type,entity_id):
        list_of_entities = self.ENTITY_MAPPING[entity_type]
        ids = [x for x in list_of_entities]
        if entity_id in ids:
            self.watchlist_coins.remove(entity_id)
        else:
            print(f"Can't remove coin {entity_id} from watchlist entity of type {entity_type} not in watchlist")

    def perform_watch_list_coin_action(self, action, entity_type,entity_id):
        VALID_ACTIONS = {'remove':self.remove_from_watchlist,'add':self.add_to_watchlist}
        VALID_ENTITY_TYPE = ['alert','coin']

        if action in VALID_ACTIONS and entity_type in VALID_ENTITY_TYPE:
            action_fuc = VALID_ACTIONS[action]
            action_fuc(entity_type, entity_id)
        self.save_changes()

    def save_changes(self):
        update_query = {'$set':{'watched_coins':[x for x in self.watchlist_coins],'alerts':[x for x in self.alerts]}}
        db['user_info'].update_one({'user_id':self.user_id},update_query)
# user_id= "1"
# wl = WatchList(user_id)
# print(wl.watchlist_coins)

# entity_id= "61f5814d32e2534f6e8e0d70"
# entity_type= "coin"
# action="add"

# wl.perform_watch_list_coin_action(action,entity_type,entity_id)
# print(wl.watchlist_coins)