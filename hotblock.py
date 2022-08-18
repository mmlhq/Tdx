# -*- coding: GBK-*- #

# ������ҳÿ��仯��������ֻ��ÿ������
# ����ǽ����գ��������˳�

import datetime
import pymysql
import requests
import json
from bs4 import BeautifulSoup
import re
import baostock as bs
import time

today = datetime.date.today()

#### ��½ϵͳ ####
lg = bs.login()
# ��ʾ��½������Ϣ
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### ��ȡ��������Ϣ ####
rs = bs.query_trade_dates(start_date=today)
print('query_trade_dates respond error_code:'+rs.error_code)
print('query_trade_dates respond  error_msg:'+rs.error_msg)

data_list = []
while (rs.error_code == '0') & rs.next():
    # ��ȡһ����¼������¼�ϲ���һ��
    data_list.append(rs.get_row_data())

isTradeday = data_list[0][1]

if isTradeday == "1":
    with open("config/config.json",encoding="utf-8") as f:
        cfg = json.load(f)
    info = cfg["mysql"]

    cnx = pymysql.connect(user=info["user"],password=info["password"],host=info["host"],database=info["database"])
    cur_block = cnx.cursor()
    cur_block_select = "select block,prevdate from tdx.hotblock where block=%s;"

    url = "https://www.eastmoney.com"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, "
                             "like Gecko) Chrome/104.0.0.0 Safari/537.36"}

    response = requests.get(url=url,headers=headers)
    soup = BeautifulSoup(response.content,"lxml")

    contents = soup.select(".ts-hot-con a")
    for item in contents:
        block = re.findall('(.+(?=���))',item.text)
        if block != []:
            cur_block.execute(cur_block_select,block)
            database_block = cur_block.fetchone()
            if database_block is not None:
                if database_block[1] != today:
                    # ����prevdate��count
                    days = (today - datetime.datetime.strptime(database_block[1],"%Y-%m-%d").date()).days
                    cur_block_update = "update `hotblock` set `prevdate`='%s',`count`=%d where `block`='%s';"%(today.strftime("%Y-%m-%d"),days,block[0])
                    cur_block.execute(cur_block_update)
                    cnx.commit()
            else:
                # ���뵱ǰ�����Ϣ (block,prevdate,count)
                cur_block_insert = "insert into `hotblock`(`block`,`prevdate`,`count`) values('%s','%s',%d)" % (block[0], today, 0)
                cur_block.execute(cur_block_insert)
                cnx.commit()
    cur_block.close()
    cnx.close()

bs.logout()