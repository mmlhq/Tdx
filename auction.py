#-*- coding: UTF-8 -*-
# 爬取东财网竞价（9:15-9:30）期间出现的涨幅超过8%的股票，写入tdx.auction表

import datetime
import pymysql
import requests
import json
import re
from bs4 import BeautifulSoup
import re
import baostock as bs
from apscheduler.schedulers.blocking import BlockingScheduler

def import_data():
    today = datetime.date.today()

    lg = bs.login()
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    rs = bs.query_trade_dates(start_date=today)
    print('query_trade_dates respond error_code:' + rs.error_code)
    print('query_trade_dates respond  error_msg:' + rs.error_msg)

    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())

    isTradeday = data_list[0][1]

    if isTradeday == "1":
        headers = {'Referer': 'https://finance.sina.com.cn'}
        # url='https://hq.sinajs.cn/list=sz002927'

        with open("config/config.json", encoding="utf-8") as f:
            cfg = json.load(f)
        info = cfg["mysql"]
        cnx = pymysql.connect(user=info["user"], password=info["password"], host=info["host"],
                              database=info["database"])
        cur_index = cnx.cursor()
        index_sql = "select code from tdx.index2 where type='1';"
        cur_index.execute(index_sql)
        database_index = cur_index.fetchall()

        cur_auction = cnx.cursor()
        cur_auction_insert = "insert into auction(code,a_date,a_price,a_gains) values('%s','%s','%s','%f')"
        time1 = '09:30:00'
        for item in database_index:
            time2 = datetime.datetime.now().strftime("%H:%M:%S")
            if time2 >= time1:
                break;
            code = item[0]
            url = 'https://hq.sinajs.cn/list=' + re.sub('[.]', '', code)
            file = requests.get(url=url, headers=headers)
            parts = file.text.split(',')
            preclose_price = float(parts[2])

            filename = code + ".txt"
            with open(filename, "wb") as f:
                f.write(file.content)

            buy1_price = float(parts[6])
            if preclose_price is not None and preclose_price != 0:
                a_gains = (buy1_price - preclose_price) / preclose_price * 100
                if a_gains >= 8:
                    cur_auction.execute(cur_auction_insert % (code, time2, buy1_price, a_gains))
                    cnx.commit()

        cur_index.close()
        cnx.close()

    bs.logout()

def dojob():
    scheduler = BlockingScheduler()
    scheduler.add_job(import_data,'cron',hour=9,minute=16)
    scheduler.start()

dojob()