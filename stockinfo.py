# -*- coding: GBK-*- #
###  1. 更新基本数据 ###

import baostock as bs
import pymysql
import json

def Update_stock_basic():
    lg = bs.login()

    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    # 连接本地数据库
    with open("config/config.json",encoding="utf-8") as f:
        cfg = json.load(f)
    info = cfg["mysql"]
    cnx = pymysql.connect(user=info["user"],password=info["password"],host=info["host"],database=info["database"])
    cur_index = cnx.cursor()
    index_stock_basic_sql = "select code,code_name,ipoDate,outDate,type,status from tdx.index2;"
    cur_index.execute(index_stock_basic_sql)
    database_index_stock_basic = cur_index.fetchall() # 元组项的元组（（code,tradeStatus,code_name），...）
    database_index_codes = [x[0] for x in database_index_stock_basic]

    stock_basic_info = ['code','code_name','ipoDate','outDate','type','status']

    update_sql = "UPDATE  `index2` SET `code_name`=%s,`outDate`=%s,`type`=%s,`status`=%s where `code`=%s; "

    for code in database_index_codes:
        rs = bs.query_stock_basic(code)
        data_list = rs.get_row_data()
        if data_list != [] :
            if data_list[3] == '':
                data_list[3] = None
            if tuple(data_list) not in database_index_stock_basic:
                rs_item = (data_list[1],data_list[3],data_list[4],data_list[5],code)
                cur_index.execute(update_sql,rs_item)
                cnx.commit()

    cnx.close()
    bs.logout()

Update_stock_basic()