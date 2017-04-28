#coding:utf-8

import threading
import ConfigParser
from warnings import filterwarnings
import MySQLdb
import sqlite3

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

    def __init__(self, db="mysql"):
        '''utf-8编码'''
        self.parser = ConfigParser.ConfigParser()
        self.parser.read("db/config.cfg")
        self.db = db
        if db == "mysql":
            self.dbname = self.parser.get("DB_Config", "database_name")
            self.conn = self.create_mysql_conn()
        if db == "sqlite":
            self.dbname = "result"
            self.conn = self.create_sqlite_conn()
        self.cursor = self.conn.cursor()
        self.connect_database()

    def create_mysql_conn(self):
        conn = MySQLdb.connect(
            host=self.parser.get("DB_Config", "database_host"),
            port=int(self.parser.get("DB_Config", "database_port")),
            user=self.parser.get("DB_Config", "database_username"),
            passwd=self.parser.get("DB_Config", "database_password"),
            charset='utf8',
            )
        return conn

    def create_sqlite_conn(self):
        conn = sqlite3.connect("db/dbfile/result.db")
        conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        return conn

    def connect_database(self):
        if self.db == "mysql":
            sql = "use %s"%self.dbname
            self.cursor.execute(sql)
        print "Database: connect %s success!"%self.dbname

    @locked(lock)
    def reconnect_database(self):
        '''
        :summary:重连接数据库
        '''
        if self.db == "mysql":
            self.conn = self.create_mysql_conn()
        if self.db == "sqlite":
            self.conn = self.create_sqlite_conn()
        self.cursor = self.conn.cursor()
        self.cursor.execute("use %s"%self.dbname)
        print "Database: reconnect %s success!"%self.dbname

    def create_mysql_db(self):
        try:
            sql = "create database if not exists %s character set utf8"%self.dbname
            self.cursor.execute(sql)
            print "Database: create database %s successed!"%self.dbname
        except MySQLdb.Warning, e:
            print e

    def __get_last_insert_item(self):
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
    def change_many_mysql(self, sql, paras):
        '''
        :param sql:不管什么类型，统一用%s作占位符的sql
        :param para:tuple或者list
        :return:插入到了第几行
        '''
        self.cursor.executemany(sql, paras)
        self.conn.commit()
        pid = self.__get_last_insert_item()
        return pid

    @locked(lock)
    def change_many(self, sql, paras):
        for para in paras:
            temp = sql
            for value in para:
                if isinstance(value, unicode):
                    value = "'%s'"%value.encode("utf-8")
                elif isinstance(value, float):
                    value = str(value)
                temp = temp.replace("%s", value, 1)
            try:
                self.cursor.execute(temp)
            except:
                print temp
                raise
        self.conn.commit()

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
        #判断sqlite中表是否存在
        if self.db == "sqlite":
            check = '''
            select * from sqlite_master where type='table' and name='%s'
            '''%tablename
            self.cursor.execute(check)
            results = self.cursor.fetchall()
            if not results:
                self.cursor.execute(sql)
                print "Database: create table %s succeeded in '%s'!"%(tablename, self.dbname)
            else:
                print "Database: table %s already existed in '%s'!"%(tablename, self.dbname)
            return

        #判断mysql中表是否存在
        check = "show tables"
        self.cursor.execute(check)
        results = self.cursor.fetchall()
        tables = []
        for result in results:
            tables.append(result[0].encode("utf-8"))
        if tablename not in tables:
            self.cursor.execute(sql)
            print "Database: create table %s succeeded in '%s'!"%(tablename, self.dbname)
        else:
            print "Database: table %s already existed in '%s!'"%(tablename, self.dbname)

    @locked(lock)
    def create_index(self, tablename, colname, indexname):
        if self.db == "sqlite":
            check = "select * from sqlite_master where type='index'and tbl_name='%s'"\
            %tablename
            self.cursor.execute(check)
            results = self.cursor.fetchall()
            if results != []:
                if indexname in results[0]:
                    return
        if self.db == "mysql":
            self.cursor.execute("show index from %s"%tablename)
            results = self.cursor.fetchall()
            print results
        sql = "create index %s on %s(%s)"%(indexname, tablename, colname)
        self.cursor.execute(sql)

    @locked(lock)
    def execute_sql(self, sql, mesg):
        try:
            self.cursor.execute(sql)
            print mesg
        except:
            print sql
            raise

    def clean_tables(self, tablenames):
        '''
        :param tablenames:要清除的表名
        '''
        try:
            for tablename in tablenames:
                self.cursor.execute("drop table if existed %s"%tablename)
                print "Database: drop table %s succeeded!"
        except:
            raise

if __name__ == '__main__':
    pass
