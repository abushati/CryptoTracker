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
        # self.run_interval = 60
        
        self.coin_pair_cache = {}
        

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


# from coin.api import CBClient
# from coin.coinpair import CoinPair

# from utils.db import coin_history_collection, coin_info_collection
# from utils.redis_handler import redis

# from datetime import datetime, timedelta
# import time
# import eventlet
# import asyncio
# from bson.objectid import ObjectId
# # from concurrent.futures import ThreadPoolExecutor
# import concurrent.futures
# from concurrent.futures import wait


# class FailedToFetchCoinPrice(Exception):
#     pass


# class CoinHistoryUpdater:

#     def __init__(self):
#         self.cache = redis()
#         self.api_client = CBClient()
#         self.history_col = coin_history_collection
#         self.coin_col = coin_info_collection
#         self.run_interval = 60

#     def load_all_coins(self):
#         # The source of where we get the data donesn't effect the speed in returning the data. have to look into the
#         # initializing of each coin pair
#         cache_key = 'coin_pairs'
#         cached_pairs = self.cache.get(cache_key)
#         if not cached_pairs:
#             print('Fetching from db')
#             res = self.coin_col.find({},{'_id':1})
#             coin_pairs_ids = [str(x['_id']) for x in res]
#             self.cache.set(cache_key,','.join(coin_pairs_ids))
#             # yield [CoinPair(pair) for pair in coin_pairs_ids]
#             return [CoinPair(pair) for pair in coin_pairs_ids]
#         else:
#             print('Fetching from cache')
#             # for pair in cached_pairs.decode("utf-8").split(','):
#             #     yield CoinPair(pair)
#             return [CoinPair(pair) for pair in cached_pairs.decode("utf-8").split(',')]

#     # async def get_current_values(self, coin: CoinPair):
#     #     info = {'price':None,'volume':None}
#     #     info['price'] = coin.current_price(include_time=True)
#     #     return info
#     # #temp
#     # async def update_history_col(self,pair,history_type,new_info):
#     #     print(f'writing to db {pair.coin_pair_sym}')
#     #     updatible_fields = {'average': lambda x: sum(x) / len(x),
#     #                         'min_value': lambda x: min(x),
#     #                         'max_value': lambda x: max(x)}
#     #
#     #     col_field = history_type
#     #     fetched_time = datetime.utcnow()
#     #     insert_time_key = fetched_time.strftime('%Y-%m-%d %H:00:00')
#     #     query = {'time': insert_time_key,
#     #              'coin_id': ObjectId(pair.pair_id),
#     #              'type': history_type}
#     #
#     #     res = self.history_col.find_one(query,{col_field:1})
#     #     history_values = res.get(col_field) or []
#     #     history_price_values = [x.get('price') for x in history_values]
#     #
#     #     updates = {}
#     #     if len(history_price_values) == 0:
#     #         updates = {x: new_info for x in updatible_fields}
#     #     else:
#     #         for key, func in updatible_fields.items():
#     #             updates[key] = func(history_price_values)
#     #
#     #         self.history_col.find_one_and_update(query,
#     #                                              {'$push': {col_field: new_info},
#     #                                               '$set': updates},
#     #                                              upsert=True)
#     #     await asyncio.sleep(1)
#     #     print(f'finished writing to db {pair.coin_pair_sym}')
#     # async def update_coin(self,coin):
#     #     print(f'updating pair {coin.pair_id}')
#     #     try:
#     #         current_values = await self.get_current_values(coin)
#     #     except FailedToFetchCoinPrice as e:
#     #         print(f'Failed to get coin-pair current value, skipping {coin}, {e}')
#     #         return
#     #
#     #     for key, current_value in current_values.items():
#     #         if current_value:
#     #             await self.update_history_col(coin, key, current_value)
#     #
#     # async def run(self, fast= True):
#     #     print('Loading coins for history update')
#     #     coins = self.load_all_coins()
#     #
#     #     while True:
#     #         if fast:
#     #             for coin in coins:
#     #                 asyncio.create_task(self.update_coin(coin))
#     #                 # try:
#     #                 #     await asyncio.create_task(self.update_coin(coin))
#     #                 # except Exception as e:
#     #                 #     print(f'Failed to update coin {coin.pair_id} {e}')
#     #         else:
#     #             for coin in coins:
#     #                 await self.update_coin(coin)
#     #                 # try:
#     #                 #     await self.update_coin(coin)
#     #                 # except Exception as e:
#     #                 #     print(f'Failed to update coin {coin.pair_id} {e}')
#     #         break
#     #         print(f'sleeping for {self.run_interval}')
#     #         time.sleep(self.run_interval)


#     # temp

#     def get_current_values(self, coin: CoinPair):
#         try:
#             price = float(self.api_client.get_coin_current_price(coin.coin_pair_sym))
#             time = datetime.utcnow()
#             #Todo: raise and catch 429 errors
#         except Exception as e:
#             print(f'failed to get price {e}')
#             raise FailedToFetchCoinPrice

#         info = {'price':None,'volume':None}
#         info['price'] = {'price':price,'time':time}
#         return info


#     def insert_new_history_doc(self, doc):
#         doc_id = self.history_col.insert_one(doc).inserted_id
#         return self.history_col.find_one({'_id':ObjectId(doc_id)})

#     def update_history_col(self,pair,history_type,new_info):
#         updatible_fields = {'average': lambda x: sum(x) / len(x),
#                             'min_value': lambda x: min(x),
#                             'max_value': lambda x: max(x)}

#         col_field = history_type
#         fetched_time = datetime.utcnow()
#         insert_time_key = fetched_time.strftime('%Y-%m-%d %H:00:00')
#         query = {'time': insert_time_key,
#                  'coin_id': ObjectId(pair.pair_id),
#                  'type': history_type}

#         res = self.history_col.find_one(query)
#         new_doc_created = False
#         if not res:
#             res = self.insert_new_history_doc(query)
#             new_doc_created = True

#         history_values = res.get(col_field) or []
#         history_price_values = [x.get('price') for x in history_values]
#         updates = {}
#         # If the doc is new, insert the new_info price, not the the CoinPrice enum
#         if new_doc_created:
#             updates = {x: new_info.price for x in updatible_fields}
#         else:
#             for key, func in updatible_fields.items():
#                 updates[key] = func(history_price_values)

#         self.history_col.find_one_and_update(query,
#                                              {'$push': {col_field: new_info},
#                                               '$set': updates})
#         print(f'Writing to update to db for {pair.coin_pair_sym}')

#     def update_coin(self,coin):
#         print(f'updating pair {coin.pair_id}')
#         try:
#             current_values = self.get_current_values(coin)
#         except FailedToFetchCoinPrice as e:
#             self.retry_coinpairs.append(coin)
#             print(f'Failed to get coin-pair current value, skipping {coin}, {e}')
#             return

#         for key, current_value in current_values.items():
#             if current_value:
#                 self.update_history_col(coin, key, current_value)

#     def _chunk_coinpairs(self,coins,chunk_size = 15):
#         chunks = []
#         chunk = []
#         for coin in coins:
#             if len(chunk) == chunk_size:
#                 chunks.append(chunk)
#                 chunk = []
#             chunk.append(coin)
#         return chunks

#     def _run(self,executor,chunks,retry=0):
#         if retry >= 4:
#             return

#         self.retry_coinpairs = []
#         #Todo; what happens to the coins loaded in the end. will they ever get updated if 1 or 10 coins don't get update
#         for chunk in chunks:
#             futures = []
#             for coin in chunk:
#                 futures.append(executor.submit(self.update_coin, (coin)))
#                 # self.update_coin(coin)
#             wait(futures)
#             time.sleep(.4)

#         if len(self.retry_coinpairs) > 0:
#             print(f'Remaining {len(self.retry_coinpairs)}')
#             new_chunks = self._chunk_coinpairs(self.retry_coinpairs, chunk_size=10)
#             self._run(executor, new_chunks, retry=retry+1)

#     def run(self):
#         print('Loading coins for history update')
#         coins = self.load_all_coins()
#         chunks = self._chunk_coinpairs(coins)

#         while True:
#             with concurrent.futures.ThreadPoolExecutor() as executor:
#                 s = time.time()
#                 self._run(executor, chunks)
#                 print(time.time()-s)
#             time.sleep(self.run_interval)