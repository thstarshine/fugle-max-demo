import os, time, requests, json, base64, hashlib, hmac, math, logging

class Max:
    def __init__(self, config):
        self.config = config

    # MAX 交易所的 GET API 基底
    def max_base_get_request(self, path, params):
        params_string = json.dumps(params, separators=(',', ':')).encode('utf-8')
        payload = base64.b64encode(params_string)
        signature = hmac.new(bytes(self.config['max']['secret_key'] , 'utf-8'), msg=payload, digestmod=hashlib.sha256).hexdigest()
        headers = {
            'X-MAX-ACCESSKEY': self.config['max']['access_key'],
            'X-MAX-PAYLOAD': payload.decode('ascii'),
            'X-MAX-SIGNATURE': signature,
            'Content-Type': 'application/json',
        }
        r = requests.get(self.config['max']['max_api_base_url']+path, headers=headers)
        return r.json()

    # MAX 交易所的 POST API 基底
    def max_base_post_request(self, path, params):
        params_string = json.dumps(params, separators=(',', ':')).encode('utf-8')
        payload = base64.b64encode(params_string)
        signature = hmac.new(bytes(self.config['max']['secret_key'] , 'utf-8'), msg=payload, digestmod=hashlib.sha256).hexdigest()
        headers = {
            'X-MAX-ACCESSKEY': self.config['max']['access_key'],
            'X-MAX-PAYLOAD': payload.decode('ascii'),
            'X-MAX-SIGNATURE': signature,
            'Content-Type': 'application/json',
        }
        r = requests.post(self.config['max']['max_api_base_url']+path, headers=headers, data=params_string)
        return r.json()

    # 取得 MAX 交易所特定幣別資訊（餘額）
    def get_max_account_info(self, currency):
        path = '/api/v2/members/accounts/' + currency
        nonce = round(time.time_ns() / 1000000)
        params = {
            'nonce': nonce,
            'path': path,
        }
        return self.max_base_get_request(path+'?nonce='+str(nonce), params)

    # 虛擬貨幣下單
    def put_max_order(self, market, side, volume, ord_type, price=""):
        path = '/api/v2/orders'
        nonce = round(time.time_ns() / 1000000)
        params = {
            'market': market,
            'side': side,
            'volume': str(volume),
            'price': str(price),
            'client_oid': str(nonce),
            'ord_type': ord_type,
            'nonce': nonce,
            'path': path,
        }
        return self.max_base_post_request(path, params)

    # 提領台幣到銀行帳戶
    def withdraw_max_twd(self, amount):
        path = '/api/v2/withdrawal/twd'
        nonce = round(time.time_ns() / 1000000)
        params = {
            'nonce': nonce,
            'amount': amount,
            'path': path,
        }
        return self.max_base_post_request(path, params)
