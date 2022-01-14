

#https://docs.cloud.coinbase.com/exchange/reference/exchangerestapi_getproducts
from coin.coin import Coin
from watchlist import WatchList, WatchListCurrencyTracker
from alerts import add_alert

ADA = Coin('ADA-USD')
add_alert('percent', 6, ADA)
