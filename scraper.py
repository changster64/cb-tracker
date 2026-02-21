import requests
import pandas as pd
import os

def send_to_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
        print(f"📡 TG 回應: {res.status_code}")
    except Exception as e:
        print(f"❌ TG 發送失敗: {e}")

def main():
    # 請務必貼上最新的「部署網址」，且最後必須是 /exec
    GAS_URL = "https://script.google.com/macros/s/AKfycbwxfiSTBhwSQJhHL3PUahtu6_llegyiGK3VYDnfh3BDNLoPvfPnXJCZNlq3FOLjYAFaXA/exec" 
    
    print(f"正在連線至 Google 跳板...")
    try:
        res = requests.get(GAS_URL, timeout=30)
        
        # 如果回傳的不是 JSON，印出前 100 個字檢查
        if "application/json" not in res.headers.get("Content-Type", ""):
            print("⚠️ Google 未回傳 JSON 格式！")
            print(f"網站回傳內容前 100 字: {res.text[:100]}")
            return

        data = res.json()
        
        # 櫃買中心資料處理
        df = pd.DataFrame(data['aaData'])
        df = df[[0, 1, 2, 4, 7]] 
        df.columns = ['Code', 'Name', 'Price', 'Change', 'Volume']
        df['Volume'] = df['Volume'].str.replace(',', '').astype(int)
        
        top5 = df.sort_values(by='Volume', ascending=False).head(5)
        
        msg = f"📊 <b>可轉債成交量前五 (最終測試)</b>\n"
        msg += f"📅 {data.get('reportDate', '今日')}\n"
        msg += "————————————————\n"
        for i, row in enumerate(top5.itertuples(), 1):
            msg += f"({i}) <code>{row.Code}</code> {row.Name}\n"
            msg += f"    價: <b>{row.Price}</b> ({row.Change}%) | 量: {row.Volume}\n"
        
        send_to_tg(msg)

    except Exception as e:
        print(f"❌ 執行失敗: {e}")

if __name__ == "__main__":
    main()
