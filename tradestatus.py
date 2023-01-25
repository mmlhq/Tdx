# -*- coding: GBK-*- #
###  1. ���½���״̬�������¹�Ʊ ###
import baostock as bs
import datetime
import pymysql
import json
from apscheduler.schedulers.blocking import BlockingScheduler


def Update_trade_status():
    lg = bs.login()

    # ��ʾ��½������Ϣ
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)
    #���ӱ������ݿ�
    with open("config/config.json", encoding="utf-8") as f:
        cfg = json.load(f)
    info = cfg["mysql"]
    cnx = pymysql.connect(user=info["user"], password=info["password"], host=info["host"], database=info["database"])
    cur_index = cnx.cursor()
    index_trade_status_sql = "select code,tradeStatus,code_name from tdx.index2;"
    cur_index.execute(index_trade_status_sql)
    database_index_trade_status = cur_index.fetchall() # Ԫ�����Ԫ�飨��code,tradeStatus,code_name����...��
    database_index_codes = [x[0] for x in database_index_trade_status]

    insert_sql = "INSERT INTO `index2`(`code`,`tradeStatus`,`code_name`) Values(%s,%s,%s) "

    date = datetime.date.today() - datetime.timedelta(days=1)
    rs = bs.query_all_stock(day='2022-11-04')  #date)   # ��ѯ����״̬,ȱʡ�ǵ�ǰʱ��
    while (rs.error_code == '0') & rs.next():
        rs_item = rs.get_row_data()
        rs_item_code = rs_item[0]
        if rs_item_code not in database_index_codes:  # ���ݿ��л�û�иù�Ʊ��Ϣ�������
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
