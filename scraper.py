import requests
import pandas as pd
import os

def send_to_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

def main():
    # 請確保這是最新的 /exec 網址
    GAS_URL = "https://script.google.com/macros/s/AKfycbxJ9-pl5JRNSnA_E-Q_cuoiFgjFfhATmoFc_Q_QR86O_OoRZgOtO87lBaaY5ju53O5P3Q/exec" 
    
    print("正在透過 Google 跳板抓取...")
    try:
        res = requests.get(GAS_URL, timeout=30)
        
        # 除錯：印出內容類型
        print(f"回應類型: {res.headers.get('Content-Type')}")
        
        # 檢查是否為有效的 JSON
        try:
            data = res.json()
        except Exception:
            print("❌ Google 回傳的不是 JSON！")
            print(f"回傳內容前 200 字: {res.text[:200]}")
            return

        if 'error' in data:
            print(f"❌ GAS 腳本報錯: {data['error']}")
            return

        # 資料處理
        df = pd.DataFrame(data['aaData'])
        df = df[[0, 1, 2, 4, 7]]
        df.columns = ['Code', 'Name', 'Price', 'Change', 'Volume']
        df['Volume'] = df['Volume'].str.replace(',', '').astype(int)
        
        top5 = df.sort_values(by='Volume', ascending=False).head(5)
        
        msg = f"📊 <b>可轉債成交量前五 (跳板版)</b>\n"
        msg += f"📅 {data.get('reportDate', '今日')}\n"
        msg += "————————————————\n"
        for i, row in enumerate(top5.itertuples(), 1):
            msg += f"({i}) <code>{row.Code}</code> {row.Name}\n"
            msg += f"    價: <b>{row.Price}</b> ({row.Change}%) | 量: {row.Volume}\n"
        
        send_to_tg(msg)
        print("✅ 任務完成")

    except Exception as e:
        print(f"❌ 執行出錯: {e}")

if __name__ == "__main__":
    main()
