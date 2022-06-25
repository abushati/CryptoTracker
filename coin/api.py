from collections import namedtuple
import httpx

#https://docs.cloud.coinbase.com/exchange/reference/exchangerestapi_getproducts
class CBClient:
    def __init__(self):
        self.client_id = "os.getenv()"
        self.client_secert = ''
        self.cb_token = ''

    def _call_api(self, path, method='GET'):
        with httpx.Client() as client:
            BASE_URL = "https://api.exchange.coinbase.com/"
            url = BASE_URL + path
            headers = {"Accept": "application/json"}

            if method == 'POST':
                res = client.post()
            elif method == 'GET':
                res = client.get(url,headers=headers)

            print(res)
            return res.json()

    def get_token(self,token: str):
        # pass token_path =
        pass

    def get_coins(self):
        tokens = []
        product_path = 'products'
        res = self._call_api(product_path)

        for coin in res:
            ticker=namedtuple('ticker', 'coin_name coin_id coin_display')
            tik = ticker(coin_name=coin.get('base_currency'), coin_id=coin.get('id'),coin_display=coin.get('display_name'))
            tokens.append(tik)
        return tokens

    """
    https://api.exchange.coinbase.com/products/{product_id}/stats
    {
        "high" : "0.4805",
        "last" : "0.4719",
        "low" : "0.4556",
        "open" : "0.47",
        "volume" : "89885114.62",
        "volume_30day" : "4760177485.9"
    }
    
    https://api.exchange.coinbase.com/products/{product_id}/ticker
    {
    "ask" : "0.4715",
    "bid" : "0.4714",
    "price" : "0.4714",
    "size" : "320.71",
    "time" : "2022-06-23T13:05:54.341112Z",
    "trade_id" : 76472612,
    "volume" : "85316079.13"
    }
    """

    def get_coin_state(self, coin_id):
        path = f'products/{coin_id}/stats'
        return self._call_api(path)

    def get_coin_info(self,coin_id):
        path = f'products/{coin_id}/ticker'
        return  self._call_api(path)

    def get_coin_current_price(self, coin_id):
        coin_info =  self.get_coin_info(coin_id)
        return coin_info.get('price')

    def get_all_currency_pairs(self):
        path = 'products'
        return self._call_api(path)

    def get_all_currencies(self):
        path = 'currencies'
        return self._call_api(path)
