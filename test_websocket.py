from operator import sub
import websockets, asyncio
import time
import json
from datetime import datetime
from utils.db import coin_info_collection
import pickle
from utils.redis_handler import redis

updater_queue = redis(async_mode=True)

async def fetch_tickers(websocket):
    try:
        while True:
            response = await websocket.recv()
            parsed = json.loads(response)
            res_type = parsed.get('type')
            if res_type != 'ticker':
                print(f'skipping {parsed}')
                continue
            print('fetched data')
            print(parsed)
            pickled_msg = pickle.dumps(parsed)
            await updater_queue.lpush('update', pickled_msg)

    except Exception as e:
        print(f'here {e}')


async def subscribe(coin_pairs):
        message = {
                "type": "subscribe",
                "product_ids": coin_pairs,
                "channels": ["ticker_batch"]
            }
        url = 'wss://ws-feed.exchange.coinbase.com'
        async with websockets.connect(url) as websocket:
            await websocket.send(json.dumps(message))
            await fetch_tickers(websocket)

            # while True:
                # await websocket.send(json.dumps(message))
                # response = await websocket.recv()
                # try:
                #     res = json.loads(response)
                #     print(res)
                #     if res.get('type') == 'subscriptions':
                #         print('sent new subscription')
                #         await fetch_tickers(websocket)                    
                # await fetch_tickers(websocket)
                    
                # except Exception as e:
                #     print(f'ERRORRRR {e}')
                #     continue
                
def run():
    coin_pairs = [coinpair.get('coin_pair') for coinpair in coin_info_collection.find({},{'coin_pair':1})]
    # remove = ['XRP-EUR','XRP-BTC','XRP-GBP','XRP-USD','GNT-USDC']
    # for r in remove:
    #     coin_pairs.remove(r)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(subscribe(coin_pairs))
    
run()