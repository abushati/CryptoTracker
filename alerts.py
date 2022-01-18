from enum  import Enum, auto
from datetime import datetime

class AlertType(Enum):
    PERCENT = 'percent'
    VOLUME = 'volume'

class AlertBase:
    TYPE = ''

    def __init__(self, alert_id):
        print(alert_id)
        if alert_id:
            #fetch from es
            pass
        else:
            self.threshold = None
            self.coin = None
            self.watchlist = None
        print(self.TYPE)

    def generate_alert(self, msg):
        print(f'Alert generated, of type {self.TYPE} with {msg}')

    def coin_specific(self):
        if self.coin:
            return True
        else:
            return False

    def save(self):
        print(f'Saving Alert of type {self.TYPE} with threshold {self.threshold}')

class PercentChangeAlert(AlertBase):
    TYPE = AlertType.PERCENT

    def check(self):
        if not self.coin_specific:
            print("Can't check alert that have no coin assigned")
            return

        x = self.coin.current_price.price
        price_history = reversed(self.coin.price_history)
        for price in price_history:
            value = price.price
            trigger_alert, msg, change = self.percent_change(x, value)
            if trigger_alert:
                message = "There was a {msg} for {coin_id}, change {change}".format(msg=msg,coin_id=self.coin.coin_id,change=change)
                print('old point {}, current point {}'.format(value,x))
                print(datetime.now() - price.insert_time)
                self.generate_alert(message)
                break

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
