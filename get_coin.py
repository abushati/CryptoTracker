from coin.coinpair import CoinPair,InvalidCoinPair

# def get_coinpair(coinpair_id):
#     try:
#         coinpair = CoinPair(coinpair_id)
#     except InvalidCoinPair:
#         print(f"Failed to get coinpair with coinpair id {coinpair_id}")
#         return None
#     return coinpair
#
#
# pair = get_coinpair('61f5814d32e2534f6e8e3db1')
# if not pair:
#     print('bad')
# print(pair.price(include_time=True))

coin = CoinPair.get_coinpair_by_sym('ada-usd')
print(coin.price(from_cache=False, include_time=True))