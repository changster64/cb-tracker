import requests
import pandas as pd
import os

def send_to_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    
    if not token or not chat_id:
        print("❌ 錯誤：找不到 TG_TOKEN 或 TG_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=payload)
        print(f"📡 Telegram 回應: {response.status_code}")
        if response.status_code == 200:
            print("✅ 訊息發送成功！")
        else:
            print(f"❌ 發送失敗：{response.text}")
    except Exception as e:
        print(f"❌ Telegram 發送過程出錯: {e}")

def main():
    # 增加更完整的 Headers 偽裝成真實瀏覽器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tpex.org.tw/web/bond/tradeinfo/cb/cb_dot.php"
    }
    
    url = "https://www.tpex.org.tw/web/bond/tradeinfo/cb/cb_dot.php?l=zh-tw&f=json"
    
    print("正在抓取櫃買中心資料...")
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        
        # 確保回傳內容是 JSON
        try:
            data = res.json()
        except ValueError:
            print("❌ 無法解析 JSON，網站可能回傳了阻擋頁面")
            return
        
        # 資料處理
        df = pd.DataFrame(data['aaData'])
        # 欄位：0代號, 1名稱, 2收盤, 4漲跌幅, 7成交量
        df = df[[0, 1, 2, 4, 7]] 
        df.columns = ['Code', 'Name', 'Price', 'Change', 'Volume']
        
        # 清理成交量數據
        df['Volume'] = df['Volume'].str.replace(',', '').astype(int)
        top5 = df.sort_values(by='Volume', ascending=False).head(5)
        
        # 建立訊息 (修正原本導致 SyntaxError 的引號問題)
        msg = f"📊 <b>可轉債成交量前五 ({data['reportDate']})</b>\n"
        msg += "————————————————\n"
        
        for i, row in enumerate(top5.itertuples(), 1):
            msg += f"({i}) <code>{row.Code}</code> {row.Name}\n"
            msg += f"    <b>{row.Price}</b> ({row.Change}%) 量:{row.Volume}\n"
        
        send_to_tg(msg)

    except Exception as e:
        print(f"❌ 程式執行失敗: {str(e)}")

if __name__ == "__main__":
    main()
