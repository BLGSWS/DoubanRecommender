#coding:utf-8

import threading
import ConfigParser
from warnings import filterwarnings
import MySQLdb

filterwarnings('error', category = MySQLdb.Warning)

#LOCK = threading.Lock()

def locked(lock):
    def _lock(fun):
        def __lock(*args, **kwargs):
            lock.acquire()
            res = fun(*args, **kwargs)
            lock.release()
            return res
        return __lock
    return _lock

class DBError(Exception):

    def __init__(self):
        Exception.__init__(self)
        self.uid = None
        self.sql = None

class DataBase(object):

    lock = threading.Lock()

    def __init__(self):
        '''utf-8编码'''
        self.parser = ConfigParser.ConfigParser()
        self.parser.read("db/config.cfg")
        self.dbname = self.parser.get("DB_Config", "database_name")
        self.conn = self.create_conn()
        self.cursor = self.conn.cursor()
        #self.create_database()
        self.connect_database()

    def create_conn(self):
        conn = MySQLdb.connect(
            host=self.parser.get("DB_Config", "database_host"),
            port=int(self.parser.get("DB_Config", "database_port")),
            user=self.parser.get("DB_Config", "database_username"),
            passwd=self.parser.get("DB_Config", "database_password"),
            charset='utf8',
            )
        return conn

    def connect_database(self):
        sql = "use %s"%self.dbname
        self.cursor.execute(sql)
        print "Database: connect success!"

    def reconnect_database(self):
        '''
        :summary:重连接数据库
        '''
        self.conn = self.create_conn()
        self.cursor = self.conn.cursor()
        self.cursor.execute("use %s"%self.dbname)
        print "Database: reconnect success!"

    def create_database(self):
        try:
            sql = "create database if not exists %s character set utf8"%self.dbname
            self.cursor.execute(sql)
            print "Database: creat database %s successed!"%self.dbname
        except MySQLdb.Warning, e:
            print e

    def get_last_insert_item(self):
        self.cursor.execute("SELECT @@IDENTITY AS pid")
        result = self.cursor.fetchall()
        return result[0]['pid']

    @locked(lock)
    def change_one(self, sql):
        try:
            self.cursor.execute(sql)
        except:
            print sql
            raise
        self.conn.commit()

    @locked(lock)
    def change_many(self, sql, para):
        '''
        :param sql:不管什么类型，统一用%s作占位符的sql
        :param para:tuple或者list
        :return:插入到了第几行
        '''
        self.cursor.executeall(sql, para)
        self.conn.commit()
        pid = self.get_last_insert_item()
        return pid

    @locked(lock)
    def select_one(self, sql):
        try:
            self.cursor.execute(sql)
        except:
            print sql
            raise
        result = self.cursor.fetchone()
        return result

    @locked(lock)
    def select_all(self, sql):
        try:
            self.cursor.execute(sql)
        except:
            print sql
            raise
        results = self.cursor.fetchall()
        return results

    @locked(lock)
    def create_table(self, sql, tablename):
        '''
        :param sql:建表语句
        :param tablename:表名
        '''
        try:
            self.cursor.execute(sql)
            print "DataBase: create table %s succeeded!"%tablename
        except MySQLdb.Warning, e:
            print e

    @locked(lock)
    def execute_sql(self, sql, mesg):
        try:
            self.cursor.execute(sql)
            print mesg
        except:
            print sql
            raise

if __name__ == '__main__':
    pass
