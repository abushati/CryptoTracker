from collections import namedtuple

import httpx

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

    def get_coin_info(self,coin_id):
        path = f'products/{coin_id}/ticker'
        return  self._call_api(path)

    def get_coin_current_price(self, coin_id):
        coin_info =  self.get_coin_info(coin_id)
        return coin_info.get('price')