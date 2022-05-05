from coin.coinpair import CoinPair, InvalidCoinPair

from utils.db import coin_history_collection, coin_info_collection, coinpair_ticker_data
from utils.redis_handler import redis

from datetime import date, datetime, timedelta, timezone
import time
from bson.objectid import ObjectId
from concurrent.futures import wait


class FailedToFetchCoinPrice(Exception):
    pass

class CoinHistoryUpdater:

    def __init__(self):
        self.cache = redis()
        self.history_col = coin_history_collection
        self.coin_col = coin_info_collection
        self.ticker_data_col = coinpair_ticker_data
        self.run_interval = 60
        
        self.coin_pair_cache = {}

    def load_all_coins(self):
        # The source of where we get the data donesn't effect the speed in returning the data. have to look into the
        # initializing of each coin pair
        cache_key = 'coin_pairs'
        cached_pairs = self.cache.get(cache_key)
        if not cached_pairs:
            print('Fetching from db')
            res = self.coin_col.find({},{'_id':1})
            coin_pairs_ids = [str(x['_id']) for x in res]
            self.cache.set(cache_key,','.join(coin_pairs_ids))
            # yield [CoinPair(pair) for pair in coin_pairs_ids]
            return [CoinPair(pair) for pair in coin_pairs_ids]
        else:
            print('Fetching from cache')
            # for pair in cached_pairs.decode("utf-8").split(','):
            #     yield CoinPair(pair)
            return [CoinPair(pair) for pair in cached_pairs.decode("utf-8").split(',')]

    def get_datetime_key(self):
        utc_datetime = datetime.utcnow()
        year = utc_datetime.year
        month = utc_datetime.month
        day = utc_datetime.day
        hour = utc_datetime.hour
        return datetime(year=year,month=month,day=day,hour=hour,tzinfo=timezone.utc)

    def _to_process_data(self, data):
        product_id = data.get('product_id')
        product_cache = self.coin_pair_cache.get(product_id)
        try:
            coin_pair = CoinPair.get_coinpair_by_sym(product_id)
        except InvalidCoinPair:
            print(f'Invalid product_id {product_id}, can"t process')
            return False

        if not product_cache:
            self.coin_pair_cache[product_id] = {'_id':coin_pair.pair_id, 'last_processed':datetime.utcnow()} 
            return True
        if (datetime.utcnow() - product_cache.get('last_processed')).seconds > 30:
            print(f"Adding to be processed, last processed {product_cache.get('last_processed')}, time now {datetime.utcnow()}")
            self.coin_pair_cache[product_id] = {'_id':coin_pair.pair_id, 'last_processed':datetime.utcnow()} 
            return True
        else:
            print(f"Skipping as the coinpair was recently processed, last processed {product_cache.get('last_processed')}, time now {datetime.utcnow()}")
            return False
            
    #Todo: find what other fields need cleaning, converting
    def _clean_data(self, data):
        data['time'] = datetime.strptime(data['time'],'%Y-%m-%dT%H:%M:%S.%fZ')
        data['price'] = float(data['price']) 
        data['open_24h'] = float(data['open_24h'])
        data['low_24h'] = float(data['low_24h']) 
        data['high_24h'] = float(data['high_24h']) 
        data['volume_30d'] = float(data['volume_30d']) 
        return data

    def _run(self):
        import pickle
        print('Starting to read from queue`')
        while True:
            data = self.cache.lpop('update')
            try:
                update_data = pickle.loads(data)
            except Exception as e:
                if data is None:
                    print(f'Queue is empty')
                    return
                
                print(f'Error pickling this data {data}')
                print(e)            
                continue

            update_data = self._clean_data(update_data)
            process_data = self._to_process_data(update_data)
            if not process_data:
                print(f'Skipping to proccess ticker data. SYM: {update_data["product_id"]}')
                continue

            self.ticker_data_col.insert_one(update_data)

    def run (self):
        while True:
            self._run()
            time.sleep(5)
