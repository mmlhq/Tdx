#-*- coding: UTF-8 -*-
# 根据tdx.balance中的日期，更新tdx.index2中balance列

import requests
import json
import pymysql
import re


with open("config/config.json", encoding="utf-8") as f:
    cfg = json.load(f)
info = cfg["mysql"]
cnx = pymysql.connect(user=info["user"], password=info["password"], host=info["host"],
                      database=info["database"])

cur_indexs = cnx.cursor()
cur_indexs_code_sql = "select code from tdx.index2;";
cur_indexs.execute(cur_indexs_code_sql)
tdx_indexs_code = cur_indexs.fetchall()
cur_indexs_update_balance = "update index2 set balance='%s' where code='%s';"

cur_balance = cnx.cursor()
cur_balance_code_sql = "select max(statDate),code from balance where code='%s';"

for code in tdx_indexs_code:
    # code[0]:股票代码，在tdx.balance中查找股票代码等于code[0]的year和quarter，取最近的（year,quarter)
    cur_balance.execute(cur_balance_code_sql%code[0])
    balance_pair = cur_balance.fetchone()

    # 将(year,quarter)写回tdx.indexs中的balance列
    if balance_pair[1] != None:
        cur_indexs.execute(cur_indexs_update_balance%balance_pair)
        cnx.commit()

cur_indexs.close()
cur_balance.close()
cnx.close()

