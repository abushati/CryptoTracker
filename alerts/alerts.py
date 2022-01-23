from enum  import Enum, auto
from datetime import datetime
from coin.coin import Coin
from utils.redis import redis
from utils.db import db

class AlertType(Enum):
    PERCENT = 'percent'
    VOLUME = 'volume'
    PRICE = 'price'

class NoCoinForAlert(Exception):
    pass

class AlertRunnerMixin:
    def run_check(self):
        if not self.coin_specific():
            print("Can't check alert that have no coin assigned")
            raise NoCoinForAlert

        trigger_alert,msg,change = self.check()
        if trigger_alert:
            self.generate_alert(msg)

class AlertBase:
    TYPE = ''

    def __init__(self, alert_id=None, coin=None, threshold=None):
        self.cache = redis()
        self.db = db['alerts']
        self.alert_id = alert_id

        if alert_id:
            #fetch from es
            pass
        elif coin is not None and threshold:
            self.threshold = threshold
            self.coin = coin
        else:
            self.coin = coin
            self.threshold = threshold
            print('Either an alert_id needs to be provided or a coin with the threshold')

        print(self.coin)


    def check(self):
        NotImplemented

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
        query = {'$set': {'alert_type':self.TYPE,'threshold':self.threshold,'coin_sym':self.coin}}
        self.db.find_one_and_update({'_id':self.alert_id},query)

class PercentChangeAlert(AlertBase, AlertRunnerMixin):
    TYPE = AlertType.PERCENT

    def check(self):
        #get the most recent price history
        price_history = self.coin.price_history
        current_price = price_history[0]
        current_price_val,current_price_insert_time = current_price.price, current_price.insert_time

        #Start this the one after the price we are checking
        for price in price_history[1:]:
            value = price.price
            trigger_alert, msg, change = self._percent_change(current_price_val, value)
            if trigger_alert and not self.already_alerted(current_price, price):
                message = "There was a {msg} for {coin_id}, change {change}".format(msg=msg,coin_id=self.coin.coin_id,change=change)
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
        current_price = self.coin.current_price(force=True)
        current_price_val,current_price_insert_time = current_price.price, current_price.insert_time

        if current_price_val > self.threshold:
            trigger, msg, change = True,'price greater than threshold', abs(current_price_val - self.threshold)

        elif current_price_val < self.threshold:
            trigger, msg, change = True, 'price less than threshold', abs(current_price_val - self.threshold)

        if trigger and not self.already_alerted(current_price.price, current_price.insert_time,self.threshold):
            return True,msg,change

class AlertRunner(AlertRunnerMixin):
    def __init__(self):
        self.alerts = self.get_alerts()
        self.run()

    def get_alerts(self):
        alerts = [PercentChangeAlert(coin=Coin('ADA-USD'),threshold=5),PriceAlert(coin=Coin('ADA-USD'),threshold=1),PriceAlert()]
        return alerts
    #Todo: turn this in to a greenpool with works
    def run(self):
        for alert in self.alerts:
            try:
                alert.run_check()
            except NoCoinForAlert:
                print('skipping check run for alert. no coin assigned')

class WatchlistAlert(AlertBase):
    def __init__(self,watchlist_id,coin,threshold,alert_type):
        self.watchlist_id = watchlist_id
        self.TYPE = alert_type
        super().__init__(coin=coin,threshold=threshold)

    def save(self):
        res = self.db.insert_one({'watchlist_id':self.watchlist_id})
        self.alert_id = res.inserted_id
        super().save()

def get_alerts(watchlist):
    #Tod: build alerts from ES query
    pass

# AlertRunner()

# PercentChangeAlert(coin=Coin('ADA-USD'),threshold=5).run_check()
# PriceAlert(coin=Coin('ADA-USD'),threshold=1).run_check()
WatchlistAlert('1bcb9699-781c-11ec-a3b5-1c1b0deb7f19','ADA-USD',1,'percent').save()