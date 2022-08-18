# -*- coding: GBK-*- #
import baostock as bs
import pandas as pd
import datetime

#### ��½ϵͳ ####
lg = bs.login()
# ��ʾ��½������Ϣ
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

today = datetime.date.today()

#### ��ȡ��������Ϣ ####
rs = bs.query_trade_dates(start_date=today)
print('query_trade_dates respond error_code:'+rs.error_code)
print('query_trade_dates respond  error_msg:'+rs.error_msg)

#### ��ӡ����� ####
data_list = []
while (rs.error_code == '0') & rs.next():
    # ��ȡһ����¼������¼�ϲ���һ��
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)

#### ����������csv�ļ� ####
result.to_csv("D:\\trade_datas.csv", encoding="gbk", index=False)
print(result)

#### �ǳ�ϵͳ ####
bs.logout()