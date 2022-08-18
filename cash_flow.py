# 成長能力

import baostock as bs
import pymysql
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import json

def import_data():
    # 登陆网站系统
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
    cur_index_sql = "select code,market,flatest_date from tdx.index;"
    cur_index.execute(cur_index_sql)
    code_item_list = cur_index.fetchall() # 财务更新日期元组项的元组（（code,market,flatest_date），....）

    cur_cash_flow = cnx.cursor()

    current_time = time.localtime(time.time())
    current_quarter = (current_time.tm_mon - 1) // 3 + 1  #当前日期的季度

    # 偿债能力

    cash_flow_head = ['code','pubDate','statDate','CAToAsset','NCAToAsset','tangibleAssetToAsset','ebitToInterest','CFOToOR','CFOToNP','CFOToGr','year','quarter']

    count = 0  # 親數據
    current_year = datetime.now().year  # 当前年份
    for code_item in code_item_list:
        for year in range(current_year-1,current_year+1):
            for quarter in range(1,5):
                code = code_item[1]+"."+code_item[0]
                cur_growth_sql = "select code,year,quarter from tdx.cash_flow where code='%s' and year='%d' and quarter='%d';"%(code,year, quarter)
                # 查看数据库是否已有该数据
                cur_cash_flow.execute(cur_growth_sql)
                findinfo = cur_cash_flow.fetchone()

                if findinfo is None:  # 數據庫中還沒有該數據，寫入數據庫
                    rs_cash_flow = bs.query_cash_flow_data(code=code_item[1]+"."+code_item[0], year=year, quarter= quarter)
                    while (rs_cash_flow.error_code == '0') & rs_cash_flow.next():
                        growth_list = rs_cash_flow.get_row_data()

                        insert_sql = "INSERT INTO cash_flow("
                        value_sql = "VALUES("
                        value_list = []

                        for index in range(len(growth_list)):
                            if growth_list[index] != '':
                                insert_sql += cash_flow_head[index]+','
                                value_sql += "'%s',"
                                value_list.append(growth_list[index])

                        insert_sql += 'year,quarter) '
                        value_sql += "'%s','%s')"

                        value_list.append(year)
                        value_list.append(quarter)
                        tuple_value = tuple(value_list)

                        cur_cash_flow_insert = insert_sql + value_sql

                        cur_cash_flow.execute(cur_cash_flow_insert%tuple_value)
                        cnx.commit()

                        count += 1
                        growth_list.clear()
                else:
                    continue

    cur_index.close()
    cur_cash_flow.close()
    cnx.close()

    # 登出系统
    bs.logout()

def dojob():
    scheduler = BlockingScheduler()
    scheduler.add_job(import_data,'cron',hour=11,minute=0)
    scheduler.start()

dojob()
