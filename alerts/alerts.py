from enum  import Enum, auto
from datetime import datetime
from coin.coin import Coin
from utils.redis import redis

class AlertType(Enum):
    PERCENT = 'percent'
    VOLUME = 'volume'

class AlertBase:
    TYPE = ''

    def __init__(self, alert_id=None):

        # if alert_id:
        #     #fetch from es
        #     pass
        # else:
        #     self.threshold = None
        #     self.coin = None
        #     self.watchlist = None
        self.coin = Coin('ADA-USD')
        self.threshold = 5
        self.cache = redis()

    def generate_alert(self, msg):
        print(f'Alert generated, of type {self.TYPE} with {msg}')

    def coin_specific(self):
        if self.coin:
            return True
        else:
            return False

    def save(self):
        print(f'Saving Alert of type {self.TYPE} with threshold {self.threshold}')


class AlertRunnerMixin:
    def run_check(self):
        if not self.coin_specific():
            print("Can't check alert that have no coin assigned")
            return
        self.check()

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
                self.generate_alert(message)
                break

    def already_alerted(self,current_price,old_price):
        #https://stackoverflow.com/questions/27522626/hash-function-in-python-3-3-returns-different-results-between-sessions
        '''Note: By default, the __hash__() values of str, bytes and datetime objects are “salted” with an unpredictable random value. Although they remain constant within an individual Python process, they are not predictable between repeated invocations of Python.
        This is intended to provide protection against a denial-of-service caused by carefully-chosen inputs that exploit the worst case performance of a dict insertion, O(n^2) complexity. See http://www.ocert.org/advisories/ocert-2011-003.html for details.
        Changing hash values affects the iteration order of dicts, sets and other mappings. Python has never made guarantees about this ordering (and it typically varies between 32-bit and 64-bit builds).
        See also PYTHONHASHSEED.'''
        cache_key = f'alert||{current_price.hash}||{old_price.hash}'
        if self.cache.get(cache_key):
            print('That combination has already be reported, skipping')
            return True
        else:
            self.cache.set(cache_key,'1')
            return False

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

def get_alerts(watchlist):
    #Tod: build alerts from ES query
    pass

PercentChangeAlert().run_check()