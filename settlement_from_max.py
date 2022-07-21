import os, time, requests, json, base64, hashlib, hmac, math, logging, datetime

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

# 取得明日需付的交割款
def get_tomorrow_settlement():
    settlements = sdk.get_settlements()
    logging.info(f'Settlement API response: {settlements}')
    tomorrow = (datetime.date.today() + datetime.timedelta(days=0)).strftime('%Y%m%d')
    for i in settlements:
        if i['c_date'] == tomorrow and int(i['price']) < 0:
            return int(i['price']) * -1
    return 0

# 如果明日需付交割款，則自動由 MAX 換匯相對應的 USDC 並提領至台股交割銀行帳戶
def main():
    logging.info(f'Getting tomorrow\'s settlement amount...')
    settlement = get_tomorrow_settlement()
    logging.info(f'Tomorrow\'s settlement: {settlement}\n')
    if settlement > 0:
        # 先將 USDC 換成台幣，採市價換匯，多換出 5% 的安全邊際到台幣錢包以避免手續費等問題
        crypto_currency = max_config['max']['currency']
        usdc_volume = round(float(settlement) / float(max_config['max']['exchange_rate']) * 1.05)
        logging.info(f'Changing {usdc_volume} {crypto_currency.upper()} to TWD...')
        order_result = max.put_max_order(crypto_currency + 'twd', 'sell', volume=usdc_volume, ord_type='market')
        # 測試的時候可以設定改採限價換匯
        # order_result = max.put_max_order(crypto_currency + 'twd', 'sell', volume=10, ord_type='limit', price=100)
        logging.info(f'Changing API response: {order_result}')
        # 等一段處理時間後，再檢查台幣餘額
        logging.info(f'Waiting for USD/TWD transactions...\n')
        time.sleep(5)
        # 檢查台幣餘額並提領至銀行帳戶
        twd_info = max.get_max_account_info('twd')
        balance = math.floor(float(twd_info['balance']))
        logging.info(f'TWD balance: {balance}, we need to withdraw {settlement} to the bank account')
        withdraw_result = max.withdraw_max_twd(settlement)
        logging.info(f'Withdraw API response: {withdraw_result}')

if __name__ == '__main__':
    main()
