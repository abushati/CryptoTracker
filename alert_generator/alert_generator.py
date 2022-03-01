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
        while True:
            while self.queue.llen(self.REDIS_KEY) > 0:
                alert_trigger = self.queue.lpop()
                print(alert_trigger)

            time.sleep(1)


if __name__ == "__main__":
    AlertGenerator().run()
