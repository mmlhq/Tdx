#-*- coding: UTF-8 -*-
# 爬取东方财富网的概念信息，写入tdx.index2的concept列

import re
import requests
import json
import pymysql

with open("config/config.json", encoding="utf-8") as f:
    cfg = json.load(f)
info = cfg["mysql"]
cnx = pymysql.connect(user=info["user"], password=info["password"], host=info["host"],
                      database=info["database"])

cur_concept = cnx.cursor()
cur_concept_select = "select title from tdx.concept;";
cur_concept.execute(cur_concept_select)
tdx_concept = cur_concept.fetchall()

url = "http://65.push2.eastmoney.com/api/qt/clist/get?"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, "
                                 "like Gecko) Chrome/104.0.0.0 Safari/537.36"}
params = {
    'cb': 'jQuery112409093214825695086_1674225318157',
    'pn': '1',
    'pz': '500',
    'po': '1',
    'np': '1',
    'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
    'fltt': '2',
    'invt': '2',
    'wbp2u': '3990134558939926|0|1|0|web',
    'fid': 'f3',
    'fs': 'm:90 t:3 f:!50',
    'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152,f124,f107,f104,f105,f140,f141,f207,f208,f209,f222',
    '_': '1674225318158'
}

response = requests.get(url=url,headers=headers,params=params)
msg = response.content.decode()
datas = re.findall('jQuery.+\((.+)\)', msg)

cur_concept_insert = "insert into concept(`key`,`title`) values('%s','%s');"
dict_datas = json.loads(datas[0])
concepts = dict_datas["data"]["diff"]
for concept in concepts:
    # 检测board是否在tdx.boards中，如果不在则添加
    if concept["f14"] not in tdx_concept:
        cur_concept.execute(cur_concept_insert%(concept['f12'],concept['f14']))

cnx.commit()
cnx.close()

