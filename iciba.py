#-*- coding: UTF-8 -*-
import requests
import json
import hashlib

class King(object):

    def __init__(self,word):
        self.headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
        self.sign = (hashlib.md5(("6key_web_fanyiifanyiweb8hc9s98e"+word).encode('utf-8')).hexdigest())[0:16]
        self.url = 'https://ifanyi.iciba.com/index.php?c=trans&m=fy&client=6&auth_user=key_web_fanyi&sign='+self.sign
        if self.is_chinese(word):
            self.data = {
                'from':'zh',
                'to':'en',
                'q':word
            }
        else:
            self.data = {
                'from':'en',
                'to':'zh',
                'q':word
            }

    def is_chinese(self,strs):
        for _char in strs:
            if not '\u4e00' <= _char <= '\u9fa5':
                return False
        return True

    def get_data(self):
        reponse = requests.post(url=self.url,headers=self.headers,data=self.data)
        return reponse.content

    def parse_data(self,reponse):
        dic_data = json.loads(reponse)
        print(dic_data['content']['out'])

    def run(self):
        response = self.get_data()
        self.parse_data(response)

if __name__ == '__main__':
    while True:
        word = input("请输入一个单词：")
        king = King(word)
        king.run()
