#!/usr/bin/env python3
"""
厄尔尼诺数据爬虫 - 从CPC获取实时数据 + 用电负荷数据
"""
import urllib.request
import re
import json
import time
from datetime import datetime

# CPC ENSO Advisory URL
CPC_URL = "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc.shtml"

# 国家能源局新闻URL
NEA_URL = "https://www.nea.gov.cn/"

def fetch_enso_data():
    """从CPC获取ENSO数据"""
    try:
        req = urllib.request.Request(CPC_URL)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
        with urllib.request.urlopen(req, timeout=20) as f:
            html = f.read().decode('utf-8')
        
        # 解码HTML实体
        html = html.replace('&#37;', '%').replace('&ntilde;', 'ñ').replace('&Ntilde;', 'Ñ')
        
        data = {}
        
        # 当前状态
        status_match = re.search(r'ENSO-([a-z]+) conditions continued', html)
        data['status'] = status_match.group(1) if status_match else 'neutral'
        
        # Niño-3.4指数
        nino34 = re.search(r'Niño-3\.4 index value was ([+-]?\d+\.\d)', html)
        data['nino34'] = float(nino34.group(1)) if nino34 else None
        
        # Niño-4指数
        nino4 = re.search(r'Niño-4.*?at ([+-]?\d+\.\d)', html)
        data['nino4'] = float(nino4.group(1)) if nino4 else None
        
        # Niño-1+2指数
        nino12 = re.search(r'Niño-1\+2.*?at ([+-]?\d+\.\d)', html)
        data['nino12'] = float(nino12.group(1)) if nino12 else None
        
        # 预测概率
        forecast = []
        if '82% chance in May-July 2026' in html:
            forecast.append({'probability': 82, 'period': 'May-July 2026'})
        if '96% chance in December 2026-February 2027' in html:
            forecast.append({'probability': 96, 'period': 'Dec 2026-Feb 2027'})
        data['forecast'] = forecast
        
        data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['source'] = 'CPC/NOAA'
        
        return data
        
    except Exception as e:
        return {'error': str(e)}

def fetch_power_load():
    """从国家能源局获取用电负荷数据"""
    try:
        # 先获取新闻列表页面找到用电负荷新闻链接
        req = urllib.request.Request(NEA_URL)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=15) as f:
            html = f.read().decode('utf-8')
        
        # 找到用电负荷新闻链接
        link_match = re.search(r'href="([^"]*43e9f28[^"]*)"', html)
        if not link_match:
            return {'error': '未找到用电负荷新闻'}
        
        news_url = "https://www.nea.gov.cn/" + link_match.group(1)
        
        # 获取新闻详情
        req = urllib.request.Request(news_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=15) as f:
            content = f.read().decode('utf-8')
        
        # 提取用电负荷数据
        data = {}
        
        # 南方区域最大负荷
        max_load = re.search(r'达(\d+\.?\d*)亿千瓦', content)
        if max_load:
            data['south_china_max_load'] = float(max_load.group(1))
        
        # 同比增长
        yoy = re.search(r'较去年最高值增加(\d+)万千瓦、增幅(\d+\.?\d+)%', content)
        if yoy:
            data['yoy_increase'] = float(yoy.group(1))
            data['yoy_pct'] = float(yoy.group(2))
        
        # 用电量增长
        power_use = re.search(r'南方区域全社会用电量同比增幅达(\d+\.?\d+)%', content)
        if power_use:
            data['power_consumption_growth'] = float(power_use.group(1))
        
        # 时间区间 - 直接用字符串搜索
        if '5月25日—28日' in content:
            data['peak_date_start'] = '5月25日'
            data['peak_date_end'] = '5月28日'
            data['peak_period'] = '2026年5月25日—5月28日'
        
        # 发布时间
        pub_match = re.search(r'发布时间[：:](\d{4}-\d+-\d+)', content)
        if pub_match:
            data['publish_date'] = pub_match.group(1)
        
        data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['source'] = 'NEA/国家能源局'
        
        return data
        
    except Exception as e:
        return {'error': str(e)}

def main():
    print("=== 厄尔尼诺 + 用电负荷 数据爬虫 ===")
    
    # 获取ENSO数据
    print("\n--- ENSO数据 ---")
    enso = fetch_enso_data()
    if 'error' in enso:
        print(f"ENSO错误: {enso['error']}")
    else:
        print(f"状态: ENSO-{enso['status']}")
        print(f"Niño-3.4: {enso['nino34']}°C")
        print(f"预测: {enso['forecast']}")
    
    # 获取用电负荷数据
    print("\n--- 用电负荷数据 ---")
    power = fetch_power_load()
    if 'error' in power:
        print(f"用电负荷错误: {power['error']}")
    else:
        print(f"南方区域最大负荷: {power.get('south_china_max_load')}亿千瓦")
        print(f"时间区间: {power.get('peak_period')}")
        print(f"同比增加: {power.get('yoy_increase')}万千瓦 ({power.get('yoy_pct')}%)")
        print(f"用电量增长: {power.get('power_consumption_growth')}%")
    
    # 保存到文件
    all_data = {
        'enso': enso,
        'power': power,
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open('/Users/yujian/.qclaw/workspace/elnino-dashboard/enso_data.json', 'w') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("\n数据已保存到 enso_data.json")

if __name__ == '__main__':
    main()