import time
from utils.db import alert_generate_collection
from utils.redis_handler import generate_alert_queue

class AlertGenerator():
    REDIS_KEY = 'alert_trigger'

    def __init__(self):
        self.db = alert_generate_collection
        self.queue = generate_alert_queue()
        self.run()

    def run(self):
        print('we in here')
        while True:
            while self.queue.llen(self.REDIS_KEY) > 0:
                alert_trigger = self.queue.lpop(self.REDIS_KEY)
                print(alert_trigger)

            time.sleep(1)



AlertGenerator().run()
