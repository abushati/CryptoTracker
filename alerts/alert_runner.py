import time
from utils.db import db
from datetime import datetime
from .alerts import NoCoinForAlert, AlertFactory


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


class AlertRunner(AlertRunnerMixin):
    def __init__(self):
        self.db = db['alerts']
        self.alerts = self.get_alerts()

    def get_alerts(self):
        '''
        1) get alerts that are not long running and havn't been generated
        2) Get alerts that ARE long running, will check if the cool down period is over
        '''
        all_alerts = self.db.find({},{'alert_type':1,'_id':1})
        valid_alerts = []
        for alert in all_alerts:
            alert = AlertFactory.get_alert(alert['alert_type'], alert['_id'])
            if not alert.long_running and alert.last_generated is None:
                valid_alerts.append(alert)
            if alert.long_running and alert.last_generated:
                last_generated_time = alert.last_generated
                cool_down = alert.cool_down_period
                now = datetime.utcnow()
                if (now - last_generated_time).total_seconds() > cool_down:
                    valid_alerts.append(alert)

        return valid_alerts

    def cool_down(self):
        # Reload the alerts, removes any that have been generated
        print('Cooling alert runner')
        self.alerts = self.get_alerts()
        time.sleep(60)

    # Todo: turn this in to a greenpool with works
    def run(self):
        while True:
            if len(self.alerts) == 0:
                print('No valid alerts, rechecking in 1 min')
                self.cool_down()
            for alert in self.alerts:
                try:
                    print(f'Running check on alert {alert.alert_id}')
                    alert.run_check()
                except NoCoinForAlert:
                    print('skipping check run for alert. no coin assigned')

            self.cool_down()

if __name__ == '__main__':
    AlertRunner().run()