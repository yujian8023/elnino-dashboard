#!/usr/bin/env python3
"""获取实时期货和股票数据"""
import urllib.request
import re
import json
from datetime import datetime

# 股票代码
stock_codes = {
    "sh600737": "中粮糖业",
    "sh601118": "海南橡胶", 
    "sh600540": "新赛股份",
    "sz000911": "南宁糖业",
    "sh600251": "冠农股份",
    "sh600313": "农发种业"
}

# 期货代码（不带nf_前缀）
future_codes = {"M0": "豆粕", "RU0": "橡胶", "SR0": "白糖", "C0": "玉米", "Y0": "豆油"}

def get_stocks():
    stocks = []
    codes = ",".join(stock_codes.keys())
    url = f"http://hq.sinajs.cn/list={codes}"
    req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn'})
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        content = response.read().decode('gb2312', errors='ignore')
        
        for code, name in stock_codes.items():
            pattern = f'hq_str_{code}="([^"]+)"'
            match = re.search(pattern, content)
            if match:
                data = match.group(1).split(',')
                if len(data) >= 4:
                    price = float(data[1]) if data[1] else 0
                    prev = float(data[2]) if data[2] else 0
                    change = price - prev
                    pct = (change / prev * 100) if prev else 0
                    stocks.append({
                        "name": name,
                        "code": code.replace("sh", "").replace("sz", ""),
                        "price": f"{price:.2f}",
                        "change": f"{change:+.2f}",
                        "pct": f"{pct:+.2f}%",
                        "category": "白糖" if "糖业" in name else ("橡胶" if "橡胶" in name else "其他")
                    })
    except Exception as e:
        print(f"Stock error: {e}")
    return stocks

def get_futures():
    futures = []
    for code, name in future_codes.items():
        url = f"http://hq.sinajs.cn/list={code}"
        req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn'})
        
        try:
            response = urllib.request.urlopen(req, timeout=5)
            content = response.read().decode('gb2312', errors='ignore')
            
            pattern = f'hq_str_{code}="([^"]+)"'
            match = re.search(pattern, content)
            if match:
                data = match.group(1).split(',')
                if len(data) >= 9:
                    price = float(data[8]) if data[8] else 0  # 最新价在第8位
                    prev = float(data[5]) if data[5] else 0  # 昨收在第5位
                    if price > 0 and prev > 0:
                        change = price - prev
                        pct = (change / prev * 100) if prev else 0
                        futures.append({
                            "category": name,
                            "name": f"{name}主连",
                            "price": f"{price:.0f}",
                            "change": f"{pct:+.2f}%",
                            "status": "up" if change > 0 else "down"
                        })
        except Exception as e:
            print(f"Future {code} error: {e}")
    return futures

if __name__ == "__main__":
    stocks = get_stocks()
    futures = get_futures()
    
    with open('stock_data.json', 'w') as f:
        json.dump({"update_time": datetime.now().isoformat(), "stocks": stocks}, f, ensure_ascii=False, indent=2)
    
    with open('futures_data.json', 'w') as f:
        json.dump({"update_time": datetime.now().isoformat(), "futures": futures}, f, ensure_ascii=False, indent=2)
    
    print(f"股票: {len(stocks)}, 期货: {len(futures)}")
    for s in stocks[:3]:
        print(f"  {s['name']}: {s['price']} {s['pct']}")
    for f in futures[:3]:
        print(f"  {f['category']}: {f['price']} {f['change']}")
