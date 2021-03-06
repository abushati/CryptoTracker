from enum  import Enum, auto
from bson.objectid import ObjectId
from coin.coinpair import CoinPair, InvalidCoinPair
from utils.redis_handler import redis
from utils.db import db, alerts_collection
from datetime import datetime
import pickle


class AlertType(Enum):
    PERCENT = 'percent'
    VOLUME = 'volume'
    PRICE = 'price'

class NoCoinForAlert(Exception):
    pass

class AlertCreationError(Exception):
    pass
    # def __init__(self, alert_type, **kwargs):
    #     self.message = f"Failed creating a new alert of type {alert_type}, with the parameters {kwargs}"
    #     super().__init__(self.message)

class AlertFactory:
    @staticmethod
    def get_alert(alert_type,alert_id):
        if alert_type == AlertType.PRICE.value:
            print('here')
            alert = PriceAlert().get_alert_by_id(alert_id)
        elif alert_type == AlertType.PERCENT.value:
            alert = PercentChangeAlert().get_alert_by_id(alert_id)
        else:
            print(f'type {alert_type} id {alert_id} not valid')
            return None
        return alert


class AlertBase:
    TYPE = None
    SUPPORTED_TRACKER_TYPES = ('price','volume')

    def __init__(self):
        self.cache = redis()
        self.db = alerts_collection
        # self.get_alert_by_id(alert_id)

    @classmethod
    def create_new(cls,alert_data):
        required_alert_fields = ['coin_pair_id','tracker_type','threshold','threshold_condition']
        creation_error = False

        if not all([alert_data.get(x) for x in required_alert_fields]):
            print('Not all required alert fields have been provided')
            creation_error = True
        else:
            coin_pair_id = alert_data.get('coin_pair_id')
            tracker_type = alert_data.get('tracker_type')
            threshold = alert_data.get('threshold')
            threshold_condition = alert_data.get('threshold_condition')
            long_running = alert_data.get('long_running', False)
            cool_down_period = alert_data.get('cool_down_period', 300)

        if not (isinstance(threshold, float) or isinstance(threshold,int)):
            try:
                threshold = float(threshold)
            except:
                print('Threshold must be of type float')
                creation_error = True

        if notification_settings := alert_data.get('notification_settings'):
            notification_fields = ['method','destination_val']
            if not all([notification_settings.get(x) for x in notification_fields]):
                print('Not all required notification fields were populated')
                creation_error = True

        try:
            CoinPair.get_by_id(coin_pair_id)
        except InvalidCoinPair:
            print(f'Invalid coin pair {coin_pair_id},skipping creation')
            creation_error = True

        if creation_error:
            raise AlertCreationError

        print('Creating new alert')
        
        new_alert = cls()
        new_alert.alert_id = ObjectId()
        new_alert.coinpair_id = coin_pair_id
        new_alert.threshold = threshold
        new_alert.tracker_type = tracker_type
        new_alert.long_running = long_running
        new_alert.cool_down_period = cool_down_period
        new_alert.threshold_condition = threshold_condition
        new_alert.notification_settings = notification_settings
        new_alert.save(create_new=True)

        return new_alert

    #Todo: why is this being called on an instance and not from a class method
    def get_alert_by_id(self,alert_id):
        alert_info = self.db.find_one({'_id': ObjectId(alert_id)})
        print(alert_info)
        if not alert_info:
            print(f'No alert with that alert_id {alert_id}')
        self.alert_id = alert_id
        self.coinpair = CoinPair.get_by_id(alert_info.get('coin_pair_id'))
        self.threshold = alert_info.get('threshold')
        self.tracker_type = alert_info.get('threshold')
        self.long_running = alert_info.get('long_running', False)
        self.cool_down_period = alert_info.get('cool_down_period', 300)
        self.last_generated = alert_info.get('last_generated', None)
        self.threshold_condition = alert_info.get('threshold_condition', None)
        self.notification_settings = alert_info.get('notification_settings', None)
        return self

    #Todo: perhaps track if alert expires
    def save(self, create_new=False):
        if not self.alert_id:
            print("Can't save alert without id assigned")
            return
        
        set_info =  {'alert_type':self.TYPE.value,'threshold':self.threshold,
                          'coin_pair_id':self.coinpair_id, 'insert_time':datetime.utcnow(),
                          'long_running':self.long_running, 'threshold_condition':self.threshold_condition,
                          'notification_settings':self.notification_settings}
        #If we are creating a new alert, then we need to pass the alert id to the query that will be used in in the upsert
        if create_new:
            set_info['_id'] = self.alert_id
            print(self.alert_id)
        
        query = {'$set':set_info}        
        self.db.find_one_and_update({'_id':self.alert_id},query,upsert=create_new)


    # Todo: This function will generate an alert and mark the alert as generated. This is a one shot alert and will be dicarded
    #   from the alert runner. If the alert is long_running, will need to think about that
    def generate_alert(self, msg):
        alert_generated = True
        self.last_generated = datetime.utcnow()
        self.db.find_one_and_update({'_id':ObjectId(self.alert_id)},{'$set':{'alert_generated':alert_generated,
                                                                                 'last_generated':self.last_generated}})
        print(f'Alert generated, of type {self.TYPE.value}. Msg: {msg}')
        self.send_to_alert_genarator(msg)

    def send_to_alert_genarator(self,msg):
        data = {
            'alert_info':{
                'alert_id':self.alert_id,
                'alert_threshold': self.threshold,
                'alert_type':self.tracker_type,
                'coin_pair':self.coinpair.coin_pair_sym,
                'notification_settings':self.notification_settings
                },
            'trigger_msg':msg
        }
        pickled_msg = pickle.dumps(data)
        print(f'alert trigger sent to genarator queue {pickled_msg}')
        self.cache.rpush('alert_trigger', pickled_msg)


class PercentChangeAlert(AlertBase):
    TYPE = AlertType.PERCENT

    def run_check(self):
        trigger_alert = False
        current_pair_history = self.coinpair.price(from_cache=False, include_time=True)
        current_price_val, current_price_insert_time = current_pair_history.price, current_pair_history.insert_time
        for data in self.coinpair.pair_history('price'):
            hour_min = data.get('hour_min')
            hour_max = data.get('hour_max')

            for value in [hour_min, hour_max]:
                alert_triggered = self.trigger_alert(current_price_val,value)
                if alert_triggered:

                    print('Above threshold values found from min,max hour value')
                    return

        return trigger_alert, None, None

    def trigger_alert(self,current_price_val, value):
        gen_alert = True
        is_triggered, msg,change_value  = self._percent_change(current_price_val, value)
        if not is_triggered:
            return False

        msg = f'There is a percent {msg} greater than the threshold {self.threshold} with value of {change_value} percent change' \
              f' and current price {current_price_val}, checked with value {value} for coinpair {self.coinpair.coin_pair_sym}' \
              f'alert id = {self.alert_id}'
        if self.last_generated:
            regen_alert = self.regenerate_alert(change_value, value )
            if not regen_alert:
                gen_alert = False

        if gen_alert:
            self.generate_alert(msg)
            self.cache.set(f'generated_alert_{self.alert_id}',f'{value}:{change_value}')
            return True

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

        # If a threshold condition is provided, we want to check that. If no condition is provided we don't care if it
        # is a percent increase of decrease
        if trigger and self.threshold_condition:
            if msg != self.threshold_condition:
                trigger = False

        return trigger, msg, change

    #Todo: perhaps the cool down period (if specified) will over ride this
    def regenerate_alert(self,change_value, value):
        try:
            cached_start_value,cached_percent_change = self.cache.get(f'generated_alert_{self.alert_id}').decode("utf-8").split(':')
        except:
            return True
        percent_change_delta = abs(float(cached_percent_change)-change_value)
        if cached_percent_change == value and percent_change_delta > .5:
            print(f'SHOULD REGEN ALERT')
            return True
        print(f'SHOULD NOT REGEN ALERT')
        return False

class PriceAlert(AlertBase):
    TYPE = AlertType.PRICE

    def run_check(self):
        #get the most recent price history
        current_price = self.coinpair.price(from_cache=False, include_time=True)
        current_price_val, current_price_insert_time = current_price.price, current_price.insert_time

        alert_triggered = self.trigger_alert(current_price_val)

        if alert_triggered:
            print(f'Price alert id {self.alert_id} alert generated')
            return

    def trigger_alert(self, current_price_val):
        is_triggered, msg, change_value = self._price_threshold(current_price_val)
        if is_triggered:
            msg = f'There is a price {msg} threshold {self.threshold} with a current value of {current_price_val}'
            self.generate_alert(msg)
            return True
        return False

    def _price_threshold(self,current_price_val):
        price_diff = abs(current_price_val - self.threshold)
        if price_diff > self.threshold and self.threshold_condition == 'above':
            trigger, msg, change = True, 'greater than', price_diff
        elif price_diff < self.threshold and self.threshold_condition == 'below':
            trigger, msg, change = True, 'less than', price_diff
        else:
            trigger, msg, change = False, None, price_diff

        return trigger, msg, change

    #Todo: This function should check if an alert should be regenerated.
    # Example we don't want this alert to be generated multiple time
    # greater than the threshold 1 with value of 1.1316966322898776 percent change and current price 1.1081, checked with value 1.0957
    # each subclass should have a regenerate_alert function
    # in this case we can cache the last generation details, so two prices that triggered the alert and percent change.
    # We should check the cached values and new values and see how close they are two one another
    def regenerate_alert(self):
        pass

class WatchlistAlert(AlertBase):
    def __init__(self, watchlist_id,coin,threshold,alert_type):
        self.watchlist_id = watchlist_id
        if alert_type not in [atype.value for atype in AlertType]:
            print("Can't create alert with type {}".format(alert_type))
            return
        self.TYPE = alert_type
        super().__init__(coin=coin, threshold=threshold)

    def save(self):
        res = self.db.insert_one({'watchlist_id':self.watchlist_id})
        self.alert_id = res.inserted_id
        super().save()


# alert_data = dict(coin_pair_id='61f5814d32e2534f6e8e0ef7',
# threshold=1,
# tracker_type='price',
# threshold_condition='increase',
# notification_settings={
#     'method':'email',
#     'destination_val':'arvid.b901@gmail.com'
# })

# alert = PercentChangeAlert.create_new(alert_data)
# print(alert)
# new_alert_id = alert.alert_id
# print(new_alert_id)
# alert2 = PercentChangeAlert().get_alert_by_id(new_alert_id)
# print(new_alert_id == alert2.alert_id)
# msg = 'this is a test'
# alert2.generate_alert(msg)
# # AlertRunner().run()

# PercentChangeAlert(coin=Coin('ADA-USD'),threshold=5).run_check()
# PriceAlert(coin=Coin('ADA-USD'),threshold=1).run_check()
# WatchlistAlert('1bcb9699-781c-11ec-a3b5-1c1b0deb7f19','ADA-USD',1,'percent').save()


# PercentChangeAlert(coin_pair_id='61f5814d32e2534f6e8e0ef7',threshold=1,tracker_type='price').run_check()
# ADA-USD
# 61f5814d32e2534f6e8e0ef7