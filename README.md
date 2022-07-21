# fugle-max-demo

這是於 Taipei.py 2022/07 聚會分享所使用的 demo repo。

分享題目：加密貨幣與台股！？－打通虛實資產互換的第一哩路

https://www.meetup.com/taipei-py/events/287054538/

## 想法

使用 Fugle 富果及 MAX 交易所的 API，來自動處理台股與虛擬貨幣間的特定資產平衡需求。

## 情境

在股市及虛擬貨幣的熊市中，已經先行把多數高風險幣資產換成 USDC 存放。因美金持續升值，希望將 USDC 存款作為台股交割的預設款項來源，且若這段期間在幣圈有超額利潤的機會，能將多餘的金額匯回台股購買已有一定跌幅的全市場 ETF。

## 實際作法

* 每天 16:00 檢查富果帳戶的交割資訊，如果有應付款，就從 MAX 換相對應的 USDC 到銀行帳戶。
* 每天 17:00 檢查 MAX 的 USDC 餘額，如果高於某個數值，就自動用超額利潤掛相對應的 0050 預約單。

## 可設定參數

* 兩個排程的執行時間
* MAX 要換為台幣的虛擬幣別
* 計算超額利潤的餘額 threshold
* 預約單要交易的股票代碼

## Caveats

因為目前 Python SDK 尚無法使用 non-interactive 的方式設定證券及憑證密碼，如果需要使用排程，必須先在本地端環境執行一次登入。若要搬移執行環境，需將 keyring crypt file 同時複製到另一個環境，或重新登入一次。

可使用以下指令確認 keyring file 的位置：

```
python -c "import keyring.util.platform_; print(keyring.util.platform_.data_root())"
```

## 參考資料

* https://developer.fugle.tw/
* https://max.maicoin.com/documents/api
* https://faun.pub/howto-deploy-serverless-function-on-google-cloud-using-terraform-cbbb263571c1
* https://github.com/fingineering/GCPFunctionDevOpsDemo
