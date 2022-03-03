import datetime
import time
from utils.db import alert_generate_collection
from utils.redis_handler import generate_alert_queue

import pickle

class AlertGenerator():
    REDIS_KEY = 'alert_trigger'
    GENERATE_METHODS = (
        'email',
        'sms',
        'app_push'
    )
    def __init__(self):
        self.db = alert_generate_collection
        self.queue = generate_alert_queue()
        self.run()


    def insert_into_history(self,data):
        alert_info = data['alert_info']
        print(type(data))
        self.db.insert_one({
            'alert_id':alert_info['alert_id'],
            'coin_pair':alert_info['coin_pair'],
            'msg':data['trigger_msg'],
            'generated_time':datetime.datetime.utcnow()
        })

    def generate_alert(self,data):
        generate_method = data.get('alert_info').get('generate_method')
        if generate_method not in self.GENERATE_METHODS:
            return

        msg = data.get('trigger_mss')
        alert_func = getattr(self,f'generate_{generate_method}_alert')
        alert_func(msg)

    def generate_email_alert(self,msg):
        print(f'Generating email alert with message {msg}')

    def generate_sms_alert(self,msg):
        print(f'Generating sms alert with message {msg}')

    def generate_app_push_alert(self,msg):
        print(f'Generating app push alert with message {msg}')

    def run(self):
        print('we in here')
        while True:
            while self.queue.llen(self.REDIS_KEY) > 0:
                alert_trigger = self.queue.lpop(self.REDIS_KEY)
                data = pickle.loads(alert_trigger)
                self.insert_into_history(data)

                self.generate_alert(data)
            time.sleep(1)



AlertGenerator().run()
