from operator import sub
import websockets, asyncio
import time
import json
from datetime import datetime
from utils.db import coin_info_collection
async def fetch_tickers(websocket):
    print('here')
    print()
    try:
        while True:
            response = await websocket.recv()
            
            parsed = json.loads(response)
            print(parsed)
            # await asyncio.sleep(20)
            print('fetched data')
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
            while True:
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                try:
                    res = json.loads(response)
                    print(res)
                    if res.get('type') == 'subscriptions':
                        print('sent new subscription')
                        await fetch_tickers(websocket)
                except Exception as e:
                    print(f'ERRORRRR {e}')
                    continue
                
def run():
    coin_pairs = [coinpair.get('coin_pair') for coinpair in coin_info_collection.find({},{'coin_pair':1})]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(subscribe(coin_pairs))
    

# def xmit_Loop():
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         loop.run_until_complete(subscribe())
# #https://docs.cloud.coinbase.com/exchange/docs/websocket-overview
# xmit_Loop()
run()