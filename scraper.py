import requests
import pandas as pd
import os

def send_to_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

def main():
    GAS_URL = "https://script.google.com/macros/s/AKfycbz71ujsG5i0iuikC6cMO28gkaZKu1ald480dXdTVlA09opWliGn5n9cE4gWkb1jKnHo/exec" 
    
    print("正在透過 Google 跳板抓取資料...")
    try:
        res = requests.get(GAS_URL, timeout=40)
        data = res.json()
        
        # 修正：櫃買中心 API 回傳的是字串形式的 JSON，有時需要二次解析
        if isinstance(data, str):
            import json
            data = json.loads(data)

        if 'aaData' not in data:
            print(f"❌ GAS 回傳異常內容: {data}")
            return

        df = pd.DataFrame(data['aaData'])
        # 0:代號, 1:名稱, 2:收盤, 4:漲跌幅, 7:成交量
        df = df[[0, 1, 2, 4, 7]]
        df.columns = ['Code', 'Name', 'Price', 'Change', 'Volume']
        
        # 排除非數字的成交量並轉型
        df['Volume'] = df['Volume'].str.replace(',', '')
        df = df[df['Volume'].str.isnumeric()]
        df['Volume'] = df['Volume'].astype(int)
        
        top5 = df.sort_values(by='Volume', ascending=False).head(5)
        
        msg = f"📊 <b>可轉債成交量前五</b>\n"
        msg += f"📅 {data.get('reportDate', '今日')}\n"
        msg += "————————————————\n"
        for i, row in enumerate(top5.itertuples(), 1):
            msg += f"({i}) <code>{row.Code}</code> {row.Name}\n"
            msg += f"    價: <b>{row.Price}</b> ({row.Change}%) | 量: {row.Volume}\n"
        
        send_to_tg(msg)
        print("✅ 成功發送至 Telegram！")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()
