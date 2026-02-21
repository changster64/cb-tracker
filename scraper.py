import requests
import pandas as pd
import os

def send_to_tg(text):
    # 從 GitHub Secrets 讀取變數
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    
    # 檢查變數是否存在
    if not token or not chat_id:
        print("❌ 錯誤：找不到 TG_TOKEN 或 TG_CHAT_ID，請檢查 GitHub Secrets 設定。")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=payload)
        # 在 GitHub Actions Log 中印出結果，方便排查
        print(f"📡 Telegram 伺服器回應狀態碼: {response.status_code}")
        print(f"📡 Telegram 伺服器回應內容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 訊息發送成功！")
        else:
            print("❌ 訊息發送失敗，請根據上方回應內容修正。")
    except Exception as e:
        print(f"❌ 發送過程中發生錯誤: {e}")

def main():
    # 模擬瀏覽器 Header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    url = "https://www.tpex.org.tw/web/bond/tradeinfo/cb/cb_dot.php?l=zh-tw&f=json"
    
    print("串接櫃買中心資料中...")
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        
        # 資料處理
        df = pd.DataFrame(data['aaData'])
        # 欄位說明：0:代號, 1:名稱, 2:收盤價, 4:漲跌幅, 7:成交量
        df = df[[0, 1, 2, 4, 7]] 
        df.columns = ['Code', 'Name', 'Price', 'Change', 'Volume']
        
        # 清理成交量數據並排序
        df['Volume'] = df['Volume'].str.replace(',', '').astype(int)
        top5 = df.sort_values(by='Volume', ascending=False).head(5)
        
        # 格式化訊息
        msg = f"📊 <b>可轉債成交量前五 ({data
