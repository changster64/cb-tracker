import requests
import pandas as pd
import os

def send_to_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

def main():
    # 1. 模擬瀏覽器的 Header，避免被當成爬蟲阻擋
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    url = "https://www.tpex.org.tw/web/bond/tradeinfo/cb/cb_dot.php?l=zh-tw&f=json"
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status() # 如果狀態碼不是 200 會直接跳到 except
        
        # 檢查回傳內容是否為 JSON
        data = res.json()
        
        # 2. 資料處理
        df = pd.DataFrame(data['aaData'])
        df = df[[0, 1, 2, 4, 7]] 
        df.columns = ['Code', 'Name', 'Price', 'Change', 'Volume']
        df['Volume'] = df['Volume'].str.replace(',', '').astype(int)
        
        # 3. 排序前五名
        top5 = df.sort_values(by='Volume', ascending=False).head(5)
        
        # 4. 組裝訊息格式
        msg = f"📊 <b>可轉債成交量前五 ({data['reportDate']})</b>\n"
        msg += "————————————————\n"
        for i, row in enumerate(top5.itertuples(), 1):
            msg += f"({i}) <code>{row.Code}</code> {row.Name}\n"
            msg += f"    {row.Price} ({row.Change}%) 量:{row.Volume}\n"
        
        send_to_tg(msg)
        print("發送成功！")

    except Exception as e:
        error_msg = f"❌ 抓取失敗: {str(e)}"
        print(error_msg)
        # 如果失敗了也傳個訊息告訴你，方便除錯
        # send_to_tg(error_msg) 

if __name__ == "__main__":
    main()
