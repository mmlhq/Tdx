# -*- coding: GBK-*- #
###  1. 更新交易状态，增加新股票 ###
import baostock as bs
import datetime
import pymysql
import json
from apscheduler.schedulers.blocking import BlockingScheduler

def Update_trade_status():
    lg = bs.login()

    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)
    #连接本地数据库
    with open("config/config.json", encoding="utf-8") as f:
        cfg = json.load(f)
    info = cfg["mysql"]
    cnx = pymysql.connect(user=info["user"], password=info["password"], host=info["host"], database=info["database"])
    cur_index = cnx.cursor()
    index_trade_status_sql = "select code,tradeStatus,code_name from tdx.index2;"
    cur_index.execute(index_trade_status_sql)
    database_index_trade_status = cur_index.fetchall() # 元组项的元组（（code,tradeStatus,code_name），...）
    database_index_codes = [x[0] for x in database_index_trade_status]

    insert_sql = "INSERT INTO `index2`(`code`,`tradeStatus`,`code_name`) Values(%s,%s,%s) "

    date = datetime.date.today() - datetime.timedelta(days=1)
    rs = bs.query_all_stock(day=date)   # 查询交易状态,缺省是当前时间
    while (rs.error_code == '0') & rs.next():
        rs_item = rs.get_row_data()
        rs_item_code = rs_item[0]
        if rs_item_code not in database_index_codes:  # 数据库中还没有该股票信息，则插入
            cur_index.execute(insert_sql,rs_item)
            cnx.commit()

    cur_index.close()
    cnx.close()
    lg = bs.logout()

def dojob():
    scheduler = BlockingScheduler()
    scheduler.add_job(Update_trade_status,'cron',hour=23,minute=8)
    scheduler.start()

dojob()