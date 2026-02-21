import requests
import pandas as pd
import os

def send_to_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

def main():
    # 1. 抓取櫃買中心 CB 資料
    url = "https://www.tpex.org.tw/web/bond/tradeinfo/cb/cb_dot.php?l=zh-tw&f=json"
    res = requests.get(url)
    data = res.json()
    
    # 2. 資料處理
    df = pd.DataFrame(data['aaData'])
    df = df[[0, 1, 2, 4, 7]] # 代號, 名稱, 收盤, 漲跌幅, 成交量
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

if __name__ == "__main__":
    main()
