# -*- coding: GBK-*- #
import datetime
import pymysql
import requests
import json
from bs4 import BeautifulSoup
import re
import baostock as bs
from apscheduler.schedulers.blocking import BlockingScheduler

def import_data():
    today = datetime.date.today()

    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    #### 获取交易日信息 ####
    rs = bs.query_trade_dates(start_date=today)
    print('query_trade_dates respond error_code:' + rs.error_code)
    print('query_trade_dates respond  error_msg:' + rs.error_msg)

    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())

    isTradeday = data_list[0][1]

    if isTradeday == "1":
        url = "https://www.eastmoney.com"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, "
                                 "like Gecko) Chrome/104.0.0.0 Safari/537.36"}
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.content, "lxml")
        contents = soup.select(".ts-hot-con a")
        block_web_list = [];
        for item in contents:
            block = re.findall('(.+(?=板块))', item.text)
            industry = re.findall('(.+(?=行业))', item.text)
            if block != []:
                block_web_list.append(block[0])
            if industry != []:
                block_web_list.append(industry[0])

        print(block_web_list)

        with open("config/config.json", encoding="utf-8") as f:
            cfg = json.load(f)
        info = cfg["mysql"]
        cnx = pymysql.connect(user=info["user"], password=info["password"], host=info["host"],
                              database=info["database"])

        cur_block = cnx.cursor()
        cur_block_update = "update hotblock set days = days+1 where(block, date) in (select block, date from block_v);";
        cur_block.execute(cur_block_update)

        cur_block_insert = "insert into hotblock(block,date,days) values('%s','%s','%d');"
        for item in block_web_list:
            cur_block.execute(cur_block_insert % (item, today, 0))
        cur_block.close()
        cnx.commit()
        cnx.close()

    bs.logout()

def dojob():
    scheduler = BlockingScheduler()
    scheduler.add_job(import_data,'cron',hour=13,minute=2)
    scheduler.start()

dojob()