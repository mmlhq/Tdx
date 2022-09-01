#!/bin/python3
import requests
import datetime
import json
from bs4 import BeautifulSoup
import lxml
from apscheduler.schedulers.blocking import BlockingScheduler

with open("config/config.json", encoding="utf-8") as f:
    cfg = json.load(f)
info = cfg["dingtalk"]

url1 = info["url"]
headers1 = {'Content-Type': 'application/json;charset=utf-8'}

url2="https://www.zaobao.com/realtime/china/"
headers2={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}

def test():
    contentx = "每天信息:" + str(datetime.datetime.now().date()) + "\n"
    response = requests.get(url2, headers=headers2).content.decode('utf-8')
    soup = BeautifulSoup(response, 'lxml')

    i = 0
    for item in soup.findAll("a", {"class": {"flex-1 m-eps"}}):
        i = i + 1
        messagex = str(i) + '. ' + item.text.replace('\n', '') + '\n'
        contentx = contentx + messagex

    data = {
        "msgtype": "text",
        "text": {
            "content": contentx
        },
        "at": {
            "atMobiles": [
                info["phone"]
            ],
            "isAtAll": False
        }
    }

    r = requests.post(url=url1,headers=headers1,data=json.dumps(data))
    print(r.json())

def dojob():
    scheduler = BlockingScheduler()
    scheduler.add_job(test,'cron',hour=8,minute=0)
    scheduler.start()

dojob()
