import datetime
import json
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from utils.db import alert_generate_collection
from utils.redis_handler import redis

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
        self.queue = redis()
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
        notification_settings = data.get('alert_info',{}).get('notification_settings',{})

        notification_method = notification_settings.get('method')
        destination_value = notification_settings.get('destination_val')
        if not notification_settings:
            print('No notification settings for alert, skipping')
            return
        elif notification_method not in self.GENERATE_METHODS:
            print('No valid notification method for alert, skipping')
            return
        elif destination_value is None:
            print('No notification destination value for alert, skipping')
            return

        msg = data.get('trigger_msg')
        alert_func = getattr(self, f'generate_{notification_method}_alert')
        alert_func(msg,destination_value)

    def generate_email_alert(self,msg,destination_value):
        print(f'Generating email alert with message {msg} to be sent to {destination_value}')
        import smtplib, ssl

        port = 465  # For SSL
        smtp_config = json.loads(open('config.json','r').read())
        sender_email = smtp_config.get('sender_email')
        password = smtp_config.get('password')

        subject = 'CryptoTracker Notification'
        email_text = msg

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = destination_value

        message.attach(MIMEText(email_text, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("cryptotrackernotification@gmail.com", password)
            server.sendmail(sender_email, destination_value, message.as_string())

    def generate_sms_alert(self,msg,destination_value):
        print(f'Generating sms alert with message {msg} to be sent to {destination_value}')

    def generate_app_push_alert(self,msg,destination_value):
        print(f'Generating app push alert with message {msg} to be sent to {destination_value}')

    def run(self):
        print('we in here')
        while True:
            while self.queue.llen(self.REDIS_KEY) > 0:
                alert_trigger = self.queue.lpop(self.REDIS_KEY)
                data = pickle.loads(alert_trigger)
                print(f'Alert generation data: {data}')
                self.insert_into_history(data)

                self.generate_alert(data)
            time.sleep(1)


AlertGenerator().run()
