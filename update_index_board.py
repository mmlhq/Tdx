#-*- coding: UTF-8 -*-
# 爬取东方财富网板块包含的股票，更新tdx.index2的industry列

import requests
import json
import pymysql
import re

url = "http://76.push2.eastmoney.com/api/qt/clist/get?"
params = {
    'cb':'jQuery112409731143813055116_1674055463347',
    'pn':'1',
    'pz':'400',
    'po':'1',
    'np':'1',
    'ut':'bd1d9ddb04089700cf9c27f6f7426281',
    'fltt':'2',
    'invt':'2',
    'wbp2u':'3990134558939926|0|1|0|web',
    'fid':'f3',
    'fs':'b:BK1033 f:!50',
    'fields':'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152,f45',
    '_':     '1674055463459'
}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, "
                                 "like Gecko) Chrome/104.0.0.0 Safari/537.36"}

with open("config/config.json", encoding="utf-8") as f:
    cfg = json.load(f)
info = cfg["mysql"]
cnx = pymysql.connect(user=info["user"], password=info["password"], host=info["host"],
                      database=info["database"])

cur_indexs = cnx.cursor()
cur_indexs_industry = "select industry from tdx.index2 where code='%s';";
cur_indexs_update = "update index2 set industry='%s' where code='%s';"

cur_boards = cnx.cursor()
cur_boards_select = "select * from tdx.boards;";
cur_boards.execute(cur_boards_select)
tdx_boards = cur_boards.fetchall()

for board in tdx_boards:
    BK = (board[0].split('.',1))[1]
    params['fs'] =  'b:' + BK + ' f:!50',
    response = requests.get(url=url,headers=headers,params=params)
    msg = response.content.decode()
    datas = re.findall('jQuery.+\((.+)\)',msg)
    dict_datas = json.loads(datas[0])
    diffs = dict_datas['data']['diff']
    for diff in diffs:
        #  f13: 0 深圳(sz) 1 上海(sh)， f12: 股票代码
        if diff['f13'] == 0:
            code = 'sz.'+diff['f12']
        elif diff['f13'] == 1:
            code = 'sh.'+diff['f12']
        else:
            continue

        # 在tdx中查找代码为code的股票,并在industry里添加所属board信息
        cur_indexs.execute(cur_indexs_industry%code)
        industry = cur_indexs.fetchone()
        if industry is None: # tdx里没有这个股票时
            print(code)
            continue
        else:
            if industry[0] is None:
                industry_new = board[1]
            else:
                industry_new = industry[0] + ' ' + board[1]
        cur_indexs.execute(cur_indexs_update%(industry_new,code))
        cnx.commit()


cur_boards.close()
cur_indexs.close()
cnx.close()

