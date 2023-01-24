#-*- coding: UTF-8 -*-
# 爬取东方财富网板块包含的股票，更新tdx.index2的concept列

import requests
import json
import pymysql
import re

url = "http://70.push2.eastmoney.com/api/qt/clist/get?"
params = {
    'cb': 'jQuery1124009280618077589997_1674265085449',
    'pn': '1',
    'pz': '1200',
    'po': '1',
    'np': '1',
    'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
    'fltt': '2',
    'invt': '2',
    'wbp2u': '3990134558939926|0|1|0|web',
    'fid': 'f3',
    'fs': 'b:BK0552 f:!50',
    'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152,f45',
    '_': '1674265085458'
}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, "
                                 "like Gecko) Chrome/104.0.0.0 Safari/537.36"}

with open("config/config.json", encoding="utf-8") as f:
    cfg = json.load(f)
info = cfg["mysql"]
cnx = pymysql.connect(user=info["user"], password=info["password"], host=info["host"],
                      database=info["database"])

cur_indexs = cnx.cursor()
cur_indexs_concept = "select concept from tdx.index2 where code='%s';";
cur_indexs_update = "update index2 set concept='%s' where code='%s';"

cur_concept = cnx.cursor()
cur_concept_select = "select * from tdx.concept;";
cur_concept.execute(cur_concept_select)
tdx_concept = cur_concept.fetchall()

for concept in tdx_concept:
    params['fs'] =  'b:' + concept[0] + ' f:!50',
    response = requests.get(url=url,headers=headers,params=params)
    msg = response.content.decode("utf-8")
    datas = re.findall('jQuery.+\((.+)\)',msg)
    dict_datas = json.loads(datas[0])
    total = dict_datas["data"]["total"]  # 属于concept的股票数量
    try:
        diffs = dict_datas['data']['diff']
    except:
        continue

    for diff in diffs:
        #  f13: 0 深圳(sz) 1 上海(sh)， f12: 股票代码
        if diff['f13'] == 0:
            code = 'sz.'+diff['f12']
        elif diff['f13'] == 1:
            code = 'sh.'+diff['f12']
        else:
            continue

        # 在tdx中查找代码为code的股票,并在concept里添加所属信息
        cur_indexs.execute(cur_indexs_concept%code)
        index_concept = cur_indexs.fetchone()
        if index_concept is None: # tdx里没有这个股票时
            print(code)
            continue
        else:
            if index_concept[0] is None:
                concept_new = concept[1]
            else:
                concept_new = index_concept[0] + ' ' + concept[1]
        cur_indexs.execute(cur_indexs_update%(concept_new,code))
        cnx.commit()


cur_concept.close()
cur_indexs.close()
cnx.close()

