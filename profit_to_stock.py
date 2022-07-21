import os, time, requests, json, base64, hashlib, hmac, math, logging

from utils import Max
from configparser import ConfigParser
from fugle_trade.sdk import SDK
from fugle_trade.order import OrderObject
from fugle_trade.constant import (APCode, Trade, PriceFlag, BSFlag, Action)

# 設定初始化
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
fugle_config = ConfigParser()
fugle_config.read('./config/config.ini')
max_config = ConfigParser()
max_config.read('./config/max_config.ini')
max = Max(max_config)
os.environ["PYTHON_KEYRING_BACKEND"] = "keyrings.cryptfile.cryptfile.CryptFileKeyring"

# 登入富果交易 API
sdk = SDK(fugle_config)
sdk.login()

# 取得某支台股的參考價
def get_stock_price(stock_id):
    r = requests.get(fugle_config['Fugle']['RealtimeBaseUrl']+'/intraday/meta?symbolId='+stock_id+'&apiToken='+fugle_config['Fugle']['RealtimeToken'])
    return r.json()['data']['meta']['priceReference']

# 執行台股下單交易
def buy_stock(cash):
    stock_id = fugle_config['Fugle']['Stock']
    price = get_stock_price(stock_id)
    amount = math.floor(cash / int(price))
    whole_amount = math.floor(amount / 1000)
    oddlot_amount = amount - whole_amount * 1000
    logging.info(f'Buying {stock_id}: {whole_amount} whole stock & {oddlot_amount} oddlot stock with price {price}')
    # 整股部分
    if whole_amount > 0:
        order = OrderObject(
            buy_sell = Action.Buy,
            price = price,
            stock_no = stock_id,
            quantity = whole_amount,
            ap_code = APCode.Common
        )
        order_result = sdk.place_order(order)
        logging.info(f'Order API response: {order_result}')
    # 零股部分
    if oddlot_amount > 0:
        order = OrderObject(
            buy_sell = Action.Buy,
            price = price,
            stock_no = stock_id,
            quantity = oddlot_amount,
            ap_code = APCode.IntradayOdd
        )
        order_result = sdk.place_order(order)
        logging.info(f'Order API response: {order_result}')

# 如果虛擬幣餘額高於設定，則自動執行股票買單
def main():
    crypto_currency = max_config['max']['currency']
    usdc_info = max.get_max_account_info(crypto_currency)
    profit_threshold = float(max_config['max']['profit_threshold'])
    balance = float(usdc_info['balance'])
    available_profit = balance - profit_threshold
    logging.info(f'Profit threshold: {profit_threshold}, {crypto_currency.upper()} balance: {balance}')
    logging.info(f'Available {crypto_currency.upper()} amount for buying stock: {available_profit}')
    if (available_profit > 0):
        # 保守計算 USDC 的約略台幣價值
        twd_profit = math.floor(available_profit * float(max_config['max']['exchange_rate']))
        logging.info(f'Available TWD amount for buying stock: {twd_profit}')
        # 檢查台幣餘額並下台股單
        if (twd_profit > 0):
            buy_stock(twd_profit)

if __name__ == '__main__':
    main()
