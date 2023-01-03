import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
from sqlalchemy import create_engine

class Db:
    def __init__(self):
        self.db = pymysql.connect(host="localhost", port=3306, user="root", passwd="mysql", db="JeT", charset="utf8")
        self.cursor=self.db.cursor()

    def create_engine():
        return create_engine("mysql://root:mysql@localhost/JeT", encoding="utf-8")
    
    def close(self):
        self.db.close()

    def connect(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.db.close()
        return str(result)