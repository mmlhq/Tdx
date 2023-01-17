#-*- coding: UTF-8 -*-
# 获取竞价信息
import requests

headers={'Referer':'https://finance.sina.com.cn'}
url='https://hq.sinajs.cn/list=sz002927'

response = requests.get(url=url,headers=headers)
print(response.content)