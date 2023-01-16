#-*- coding: UTF-8 -*-
import re
import requests
from bs4 import BeautifulSoup
from lxml import html

url = "http://quote.eastmoney.com/center/boardlist.html#industry_board"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, "
                                 "like Gecko) Chrome/104.0.0.0 Safari/537.36"}
#
response = requests.get(url=url,headers=headers)
# with open("money.html","wb") as f:
#     f.write(response.content)

soup = BeautifulSoup(response.content,"lxml")
print("Hello！")