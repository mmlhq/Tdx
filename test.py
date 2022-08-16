import json
import pymysql

class Tdx(object):
    def __init__(self):
        pass

    def connect():
        with open("config/config.json", encoding="utf-8") as f:
            cfg = json.load(f)
        info = cfg["mysql"]
        cnx = pymysql.connect(user=info["user"],password=info["password"],host=info["host"],database=info["database"])
        return cnx

if __name__ == "__main__":
    tdx = Tdx;
    print(tdx.connect())