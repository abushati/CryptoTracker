from enum  import Enum, auto
from bson.objectid import ObjectId
from coin.coinpair import CoinPair, InvalidCoinPair
from utils.redis_handler import redis
from utils.db import db, alerts_collection
from datetime import datetime

class AlertType(Enum):
    PERCENT = 'percent'
    VOLUME = 'volume'
    PRICE = 'price'

class NoCoinForAlert(Exception):
    pass

class AlertCreationError(Exception):
    def __init__(self, alert_type, **kwargs):
        self.message = f"Failed creating a new alert of type {alert_type}, with the parameters {kwargs}"
        super().__init__(self.message)

class AlertFactory:
    @staticmethod
    def get_alert(alert_type,alert_id):
        if alert_type == AlertType.PRICE.value:
            alert = PriceAlert(alert_id=alert_id)
        elif alert_type == AlertType.PERCENT.value:
            alert = PercentChangeAlert(alert_id=alert_id)
        else:
            print(f'type {alert_type} id {alert_id} not valid')
            return None
        return alert


class AlertRunnerMixin:
    def run_check(self):
        if not self.coin_specific():
            print("Can't check alert that have no coin assigned")
            raise NoCoinForAlert

        trigger_alert,msg,change = self.check()
        if trigger_alert:
            self.generate_alert(msg)

    def check(self):
        NotImplementedError


    def coin_specific(self):
        if self.coin:
            return True
        else:
            return False

    def already_alerted(self,*args):
        cache_key = f"{self.TYPE.value}||{'||'.join([str(x) for x in args])}"
        print(cache_key)
        if self.cache.get(cache_key):
            print('That combination has already be reported, skipping')
            return True
        else:
            self.cache.set(cache_key, '1')
            return False

class AlertBase:
    TYPE = None
    SUPPORTED_TRACKER_TYPES = ('price','volume')

    def __init__(self, alert_id=None, coin_pair_id=None, tracker_type=None, threshold=None,long_running=False):
        self.cache = redis()
        self.db = alerts_collection
        self.alert_id = alert_id
        create_new = all([coin_pair_id, tracker_type, threshold])

        if alert_id:
            alert_info = self.db.find_one({'_id':ObjectId(self.alert_id)})
            self.coinpair = CoinPair(alert_info.get('coin_pair_id'))
            self.threshold = alert_info.get('threshold')
            self.tracker_type = alert_info.get('threshold')
            self.long_running = alert_info.get('long_running',False)
        elif create_new:
            print('Creating a new alert')
            create_new = self.create_new(coin_pair_id,threshold,tracker_type, long_running)
            if create_new:
                # When the alert is created self.alert_id is assigned to from the
                # new object id when saving to mongo'
                self.__init__(alert_id=self.alert_id)
            else:
                raise AlertCreationError(self.TYPE.value, **{'alert_id': alert_id, 'coin': coin_pair_id,
                                                             'threshold': threshold,'tracker_type':tracker_type})


    def create_new(self, coin_pair_id, threshold, tracker_type,long_running):
        if tracker_type not in self.SUPPORTED_TRACKER_TYPES:
            print(f'tracker type {tracker_type} is not supported.')
            return
        try:
            self.coinpair = CoinPair(coin_pair_id)
        except InvalidCoinPair:
            print(f'Invalid coin pair {coin_pair_id},skipping creation')
            return

        alert_id = self.db.insert_one({})
        self.alert_id = alert_id.inserted_id
        self.threshold = threshold
        self.tracker_type = tracker_type
        self.long_running = long_running
        self.save()

        return True

    #Todo: perhaps track if alert expires
    def save(self):
        if not self.alert_id:
            print("Can't save alert without id assigned")
            return
        query = {'$set': {'alert_type':self.TYPE.value,'threshold':self.threshold,
                          'coin_pair_id':self.coinpair.pair_id, 'insert_time':datetime.utcnow(),
                          'long_running':self.long_running}}
        self.db.find_one_and_update({'_id':self.alert_id},query)

    # Todo: This function will generate an alert and mark the alert as generated. This is a one shot alert and will be dicarded
    #   from the alert runner. If the alert is long_running, will need to think about that
    def generate_alert(self, msg):
        alert_generated = True
        if not self.long_running:
            self.db.find_one_and_update({'_id':ObjectId(self.alert_id)},{'$set':{'alert_generated':alert_generated}})
        print(f'Alert generated, of type {self.TYPE.value}. Msg: {msg}')


class PercentChangeAlert(AlertBase, AlertRunnerMixin):
    TYPE = AlertType.PERCENT

    def run_check(self):
        trigger_alert = False
        for data in self.coinpair.pair_history('price'):
            hour_values = data.get('hour_values')
            current_type_value = hour_values[0]
            hour_min = data.get('hour_min')
            hour_max = data.get('hour_max')
            current_price_val, current_price_insert_time = current_type_value.price, current_type_value.insert_time

            for value in [hour_min, hour_max]:
                alert_triggered = self.trigger_alert(current_price_val,value)
                if alert_triggered:
                    print('Above threshold values found from min,max hour value')
                    return

        return trigger_alert, None, None

    def trigger_alert(self,current_price_val, value):
        is_triggered, msg, change_value = self._percent_change(current_price_val, value)
        if is_triggered:
            msg = f'There is a percent {msg} greater than the threshold {self.threshold} with value of {change_value} percent change' \
                  f' and current price {current_price_val}, checked with value {value} for coinpair {self.coinpair.coin_pair_sym}' \
                  f'alert id = {self.alert_id}'
            self.generate_alert(msg)
            return True
        return False

    def _percent_change(self, new_value, old_value):
        change = (float(new_value - old_value)/old_value) * 100
        trigger = False
        msg = ''
        if change > 0 and abs(change) > self.threshold:
            trigger = True
            msg = 'increase'
        elif change < 0 and abs(change) > self.threshold:
            trigger = True
            msg = 'decrease'
        return trigger, msg, change


class PriceAlert(AlertBase,AlertRunnerMixin):
    TYPE = AlertType.PRICE

    def run_check(self):
        #get the most recent price history
        current_price = self.coinpair.pair_history(most_recent=True)
        current_price_val, current_price_insert_time = current_price.price, current_price.insert_time

        alert_triggered = self.trigger_alert(current_price_val)

        if alert_triggered:
            print('Above threshold values found from min,max hour value')
            return

    def trigger_alert(self, current_price_val):
        is_triggered, msg, change_value = self._price_threshold(current_price_val)
        if is_triggered:
            msg = f'There is a price {msg} threshold {self.threshold} with value of {change_value}'
            self.generate_alert(msg)
            return True
        return False

    def _price_threshold(self,current_price_val):
        price_diff = abs(current_price_val - self.threshold)
        if current_price_val > self.threshold:
            trigger, msg, change = True, 'greater than', price_diff
        elif current_price_val < self.threshold:
            trigger, msg, change = True, 'less than', price_diff
        else:
            trigger, msg, change = False, None, price_diff

        return trigger, msg, change


class AlertRunner(AlertRunnerMixin):
    def __init__(self):
        self.db = db['alerts']
        self.alerts = self.get_alerts()


    def get_alerts(self):
        all_alerts = []
        # Only return the alerts that have not generated yet
        alerts = self.db.find({'alert_generated': { '$in': [False, None]}},{'alert_type':1,'_id':1})
        for e in alerts:
            all_alerts.append(AlertFactory.get_alert(e['alert_type'],e['_id']))

        return all_alerts

    #Todo: turn this in to a greenpool with works
    def run(self):
        for alert in self.alerts:
            try:
                alert.run_check()
            except NoCoinForAlert:
                print('skipping check run for alert. no coin assigned')


class WatchlistAlert(AlertBase):
    def __init__(self, watchlist_id,coin,threshold,alert_type):
        self.watchlist_id = watchlist_id
        if alert_type not in [atype.value for atype in AlertType]:
            print("Can't create alert with type {}".format(alert_type))
            return
        self.TYPE = alert_type
        super().__init__(coin=coin,threshold=threshold)

    def save(self):
        res = self.db.insert_one({'watchlist_id':self.watchlist_id})
        self.alert_id = res.inserted_id
        super().save()

PercentChangeAlert(coin_pair_id='61f5814d32e2534f6e8e0ef7',threshold=1,tracker_type='price').run_check()
AlertRunner().run()

# PercentChangeAlert(coin=Coin('ADA-USD'),threshold=5).run_check()
# PriceAlert(coin=Coin('ADA-USD'),threshold=1).run_check()
# WatchlistAlert('1bcb9699-781c-11ec-a3b5-1c1b0deb7f19','ADA-USD',1,'percent').save()


# PercentChangeAlert(coin_pair_id='61f5814d32e2534f6e8e0ef7',threshold=1,tracker_type='price').run_check()
# ADA-USD
# 61f5814d32e2534f6e8e0ef7