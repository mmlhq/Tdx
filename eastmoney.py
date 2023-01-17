#-*- coding: UTF-8 -*-
# 爬取东方财富网的板块信息，写入数据库

import re
import requests
import json
import pymysql

url = "http://quote.eastmoney.com/center/api/sidemenu.json"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, "
                                 "like Gecko) Chrome/104.0.0.0 Safari/537.36"}

response = requests.get(url=url,headers=headers)

# with open(r"money.html","wb") as f:
#     f.write(response.content)
# soup = BeautifulSoup(response.text,"lxml")

with open("config/config.json", encoding="utf-8") as f:
    cfg = json.load(f)
info = cfg["mysql"]
cnx = pymysql.connect(user=info["user"], password=info["password"], host=info["host"],
                      database=info["database"])

cur_boards = cnx.cursor()
cur_boards_select = "select title from tdx.boards;";
cur_boards.execute(cur_boards_select)
tdx_boards = cur_boards.fetchall()

cur_boards_insert = "insert into boards(`key`,`title`) values('%s','%s');"

datas = json.loads(response.content.decode())
boards = datas[5]["next"][2]["next"]
for board in boards:
    # 检测board是否在tdx.boards中，如果不在则添加
    if tuple([board["title"]]) not in tdx_boards:
        cur_boards.execute(cur_boards_insert%(board['key'],board['title']))

cnx.commit()
cnx.close()