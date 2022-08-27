# -*- coding: GBK-*- #

# 由于网页每天变化，本程序只能每天运行
# 如果非交易日，本程序退出

import datetime
import pymysql
import requests
import json
from bs4 import BeautifulSoup
import re
import baostock as bs
import time

today = datetime.date.today()

#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 获取交易日信息 ####
rs = bs.query_trade_dates(start_date=today)
print('query_trade_dates respond error_code:'+rs.error_code)
print('query_trade_dates respond  error_msg:'+rs.error_msg)

data_list = []
while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
    data_list.append(rs.get_row_data())

isTradeday = data_list[0][1]

if isTradeday == "0":
    url = "https://www.eastmoney.com"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, "
                             "like Gecko) Chrome/104.0.0.0 Safari/537.36"}
    response = requests.get(url=url,headers=headers)
    soup = BeautifulSoup(response.content,"lxml")
    contents = soup.select(".ts-hot-con a")
    block_list = [];
    for item in contents:
        block = re.findall('(.+(?=板块))',item.text)
        if block != []:
            block_list.append(block[0])

    with open("config/config.json",encoding="utf-8") as f:
        cfg = json.load(f)
    info = cfg["mysql"]
    cnx = pymysql.connect(user=info["user"],password=info["password"],host=info["host"],database=info["database"])

    cur_block = cnx.cursor()
    cur_block_select = "select block,date from tdx.block_v;"
 #   update hotblock set date = adddate(date, interval 1 day) where(block, date) in (select block, date from block_v);
    cur_block.execute(cur_block_select)
    data_block = cur_block.fetchall()
    for item in data_block:
        if(item[0]  in block_list):
            print(item[0])
    cur_block.close()
    cnx.close()

bs.logout()