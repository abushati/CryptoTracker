from utils.redis_handler import updater_queue
import pickle
from utils.db import db
from datetime import datetime

q = updater_queue()

col = db['coinpair_ticker_data']
r = q.lpop('update')
r = pickle.loads(r)
print(r)
#Easier to just overwrite the time, time that CB provides 'time': '2022-04-09T04:18:38.093661Z' time format that is needed datetime.datetime(2022, 4, 9, 5, 8, 6, 633827)
#Perhaps datetime.strptime to convert 
r['time'] = datetime.utcnow()
print(r)
col.insert_one(r)
print(r)
datetime.strptime