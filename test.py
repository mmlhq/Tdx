# -*- coding: GBK-*- #
import baostock as bs
import pandas as pd

# ��½ϵͳ
lg = bs.login()
# ��ʾ��½������Ϣ
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

# ��ȡ֤ȯ��������
rs = bs.query_stock_basic(code="sz.301289")
# rs = bs.query_stock_basic(code_name="�ַ�����")  # ֧��ģ����ѯ
print('query_stock_basic respond error_code:'+rs.error_code)
print('query_stock_basic respond  error_msg:'+rs.error_msg)

# ��ӡ�����
data_list = []
while (rs.error_code == '0') & rs.next():
    # ��ȡһ����¼������¼�ϲ���һ��
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)
# ����������csv�ļ�
result.to_csv("D:/stock_basic.csv", encoding="gbk", index=False)
print(result)

# �ǳ�ϵͳ
bs.logout()