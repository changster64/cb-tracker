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
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        res = requests.post(url, data=payload)
        if res.status_code == 200:
            print("✅ Telegram 通知已發送")
        else:
            print(f"❌ TG 回應錯誤: {res.text}")
    except Exception as e:
        print(f"❌ TG 發送失敗: {e}")

def main():
    # 注意：請務必替換下方網址
    GAS_URL = "https://script.google.com/home/projects/15nDaP8loMGuFMLZuyENf18GpRRO37sVWfE2e61xWNXdu6AaIPOtvw66r/exec" 
    
    if "你的_GOOGLE" in GAS_URL:
        print("❌ 錯誤：你還沒替換 GAS_URL！請放入 Google Apps Script 的部署網址。")
        return

    print("正在透過 Google 跳板抓取資料...")
    try:
        res = requests.get(GAS_URL, timeout=30)
        res.raise_for_status()
        data = res.json()
        
        if 'error' in data:
            print(f"❌ Google 腳本執行錯誤: {data['error']}")
            return

        # 櫃買中心資料解析
        df = pd.DataFrame(data['aaData'])
        df = df[[0, 1, 2, 4, 7]] 
        df.columns = ['Code', 'Name', 'Price', 'Change', 'Volume']
        df['Volume'] = df['Volume'].str.replace(',', '').astype(int)
        
        top5 = df.sort_values(by='Volume', ascending=False).head(5)
        
        msg = f"📊 <b>可轉債成交量前五 (Google 代理版)</b>\n"
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
