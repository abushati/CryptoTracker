from enum  import Enum, auto
from datetime import datetime
from coin.coinpair import CoinPair
from utils.redis import redis
from utils.db import db
from bson.objectid import ObjectId

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

class AlertRunnerMixin:
    def run_check(self):
        if not self.coin_specific():
            print("Can't check alert that have no coin assigned")
            raise NoCoinForAlert

        trigger_alert,msg,change = self.check()
        if trigger_alert:
            self.generate_alert(msg)

class AlertBase:
    TYPE = None

    def __init__(self, alert_id=None, coin_pair=None, threshold=None):
        self.cache = redis()
        self.db = db['alerts']
        self.alert_id = alert_id

        if alert_id:
            alert_info = self.db.find_one({'_id':self.alert_id})
            self.coin_pair = CoinPair(alert_info.get('coin_pair_id'))
            self.threshold = alert_info.get('threshold')
        elif coin_pair is not None and threshold is not None:
            self.create_new(coin_pair,threshold)
        else:
            raise AlertCreationError(self.TYPE.value, **{'alert_id': alert_id, 'coin': coin_pair, 'threshold': threshold})

    def create_new(self,coin_pair,threshold):
        self.threshold = threshold
        self.coin_pair = coin_pair

        alert_id = self.db.insert_one({})
        self.alert_id = alert_id.inserted_id
        self.save()


    def check(self):
        NotImplementedError

    def generate_alert(self, msg):
        print(f'Alert generated, of type {self.TYPE.value} with {msg}')

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

    def save(self):
        if not self.alert_id:
            print("Can't save alert without id assigned")
            return
        query = {'$set': {'alert_type':self.TYPE.value,'threshold':self.threshold,'coin_pair_id':self.coin_pair.pair_id}}
        self.db.find_one_and_update({'_id':self.alert_id},query)


class PercentChangeAlert(AlertBase, AlertRunnerMixin):
    TYPE = AlertType.PERCENT

    def check(self):
        # get the most recent price history
        price_history = self.coin.price_history
        current_price = price_history[0]
        current_price_val,current_price_insert_time = current_price.price, current_price.insert_time

        #Start this the one after the price we are checking
        for price in price_history[1:]:
            value = price.price
            trigger_alert, msg, change = self._percent_change(current_price_val, value)
            if trigger_alert and not self.already_alerted(current_price, price):
                message = "There was a {msg} for {coin_id}, change {change}".format(msg=msg, coin_id=self.coin.pair_id, change=change)
                print('old point {}, current point {}'.format(value,current_price))
                print(datetime.now() - price.insert_time)
                True,msg,change

        return False, 'No match',None

    def _percent_change(self, new_value, old_value):
        change = (float(new_value - old_value)/old_value) * 100
        msg = ''
        trigger_alert = False
        if change > 0 and abs(change) > self.threshold:
            trigger_alert = True
            msg = 'percent_increase'
        elif change < 0 and abs(change) > self.threshold:
            trigger_alert = True
            msg = 'percent_decrease'
        return trigger_alert, msg, change


class PriceAlert(AlertBase,AlertRunnerMixin):
    TYPE = AlertType.PRICE

    def check(self):
        #get the most recent price history
        current_price = self.coin.current_price()
        current_price_val,current_price_insert_time = current_price.price, current_price.insert_time

        if current_price_val > self.threshold:
            trigger, msg, change = True,'price greater than threshold', abs(current_price_val - self.threshold)

        elif current_price_val < self.threshold:
            trigger, msg, change = True, 'price less than threshold', abs(current_price_val - self.threshold)

        if trigger and not self.already_alerted(current_price.price, current_price.insert_time,self.threshold):
            return True,msg,change


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



class AlertRunner(AlertRunnerMixin):
    def __init__(self):
        self.db = db['alerts']
        self.alerts = self.get_alerts()


    def get_alerts(self):
        all_alerts = []
        alerts = self.db.find({},{'alert_type':1,'_id':1})
        for e in alerts:
            print(e)
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


# AlertRunner().run()

# PercentChangeAlert(coin=Coin('ADA-USD'),threshold=5).run_check()
# PriceAlert(coin=Coin('ADA-USD'),threshold=1).run_check()
# WatchlistAlert('1bcb9699-781c-11ec-a3b5-1c1b0deb7f19','ADA-USD',1,'percent').save()

PercentChangeAlert(coin_pair=CoinPair(ObjectId('61f5814d32e2534f6e8e0ef7')),threshold=9)
# ADA-USD
# 61f5814d32e2534f6e8e0ef7