import requests
import pandas as pd
import os
import time

def send_to_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    
    if not token or not chat_id:
        print("❌ 錯誤：找不到 TG_TOKEN 或 TG_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Telegram 訊息發送成功！")
        else:
            print(f"❌ Telegram 發送失敗：{response.text}")
    except Exception as e:
        print(f"❌ Telegram 發送過程出錯: {e}")

def main():
    # 改用證交所 (TWSE) 的 API 作為來源
    # 這邊抓的是「所有債券」成交資料
    url = "https://www.twse.com.tw/exchangeReport/BOND_ALL?response=json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    print("正在從證交所抓取資料...")
    try:
        res = requests.get(url, headers=headers, timeout=20)
        data = res.json()
        
        if 'data' not in data:
            print("❌ 證交所未回傳有效資料")
            return

        # 證交所回傳的欄位
        # 0:代號, 1:名稱, 2:成交張數, 3:成交金額, 4:成交價...
        df = pd.DataFrame(data['data'])
        
        # 只過濾出「可轉債」(通常代號是 5 或 6 碼且包含中文名稱有 '○' 或數字)
        # 這裡簡單先用「成交張數」來排名前五
        df = df[[0, 1, 4, 2]] 
        df.columns = ['Code', 'Name', 'Price', 'Volume']
        
        # 清理成交量 (去掉逗號轉數字)
        df['Volume'] = df['Volume'].str.replace(',', '').astype(int)
        
        # 排序前五名
        top5 = df.sort_values(by='Volume', ascending=False).head(5)
        
        # 建立訊息
        msg = f"📊 <b>可轉債成交量前五 (TWSE 版)</b>\n"
        msg += f"📅 {data['date']}\n"
        msg += "————————————————\n"
        
        for i, row in enumerate(top5.itertuples(), 1):
            msg += f"({i}) <code>{row.Code}</code> {row.Name}\n"
            msg += f"    價: <b>{row.Price}</b> | 量: {row.Volume}\n"
        
        send_to_tg(msg)

    except Exception as e:
        print(f"❌ 執行失敗: {str(e)}")
        # 如果還是失敗，嘗試印出部分內容協助除錯
        if 'res' in locals():
            print(f"網站回傳前100個字: {res.text[:100]}")

if __name__ == "__main__":
    main()
