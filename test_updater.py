# from utils.redis_handler import redis
# import pickle
# from utils.db import db
# from datetime import datetime

# q = redis()
# while True:
#     col = db['coinpair_ticker_data']
#     r = q.lpop('update')
#     r = pickle.loads(r)
#     #Easier to just overwrite the time BUT VERY WRONG, time that CB provides 'time': '2022-04-09T04:18:38.093661Z' time format that is needed datetime.datetime(2022, 4, 9, 5, 8, 6, 633827)
#     #TODO: Perhaps datetime.strptime to convert 
#     r['time'] = datetime.utcnow()
#     col.insert_one(r)

from realtime_updater.realtime_updater import run
run()