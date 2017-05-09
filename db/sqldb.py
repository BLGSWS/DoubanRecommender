#coding:utf-8

import threading
import ConfigParser

parser = ConfigParser.ConfigParser()
parser.read("db/config.cfg")
if "mysql" == parser.get("DB_Config", "database_type"):
    import MySQLdb
    from warnings import filterwarnings
    filterwarnings('error', category = MySQLdb.Warning)
else:
    import sqlite3

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

class MySqlDataBase(object):

    lock = threading.Lock()

    def __init__(self):
        '''utf-8编码'''
        self.parser = ConfigParser.ConfigParser()
        self.parser.read("db/config.cfg")
        self.dbname = self.parser.get("DB_Config", "database_name")
        self.conn = self.create_conn()
        self.cursor = self.conn.cursor()
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
        print "Database: connect %s success!"%self.dbname

    def reconnect_database(self):
        '''
        :summary:重连接数据库
        '''
        self.conn = self.create_conn()
        self.cursor = self.conn.cursor()
        self.cursor.execute("use %s"%self.dbname)
        print "Database: reconnect %s success!"%self.dbname

    def create_db(self):
        try:
            sql = "create database if not exists %s character set utf8"%self.dbname
            self.cursor.execute(sql)
            print "Database: create database %s successed!"%self.dbname
        except MySQLdb.Warning, e:
            print e

    @locked(lock)
    def change_one(self, sql):
        try:
            self.cursor.execute(sql)
        except:
            print sql
            raise
        self.conn.commit()

    @locked(lock)
    def change_many(self, sql, paras):
        '''
        :param sql:不管什么类型，统一用%s作占位符的sql
        :param para:tuple或者list
        :return:插入到了第几行
        '''
        self.cursor.executemany(sql, paras)
        self.conn.commit()
        pid = self.__get_last_insert_item()
        return pid

    def __get_last_insert_item(self):
        self.cursor.execute("SELECT @@IDENTITY AS pid")
        result = self.cursor.fetchall()
        return result[0]['pid']

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
        self.cursor.execute("show index from %s"%tablename)
        results = self.cursor.fetchall()
        if indexname not in results:
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

class SqliteDataBase(object):

    lock = threading.Lock()

    def __init__(self):
        '''utf-8编码'''
        self.dbname = "result"
        self.conn = self.create_conn()
        self.cursor = self.conn.cursor()

    def create_conn(self):
        conn = sqlite3.connect("db/dbfile/result.db")
        conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        return conn

    @locked(lock)
    def reconnect_database(self):
        '''
        :summary:重连接数据库
        '''
        self.conn = self.create_conn()
        self.cursor = self.conn.cursor()
        self.cursor.execute("use %s"%self.dbname)
        print "Database: reconnect %s success!"%self.dbname

    def create_db(self):
        pass

    @locked(lock)
    def change_one(self, sql):
        try:
            self.cursor.execute(sql)
        except:
            print sql
            raise
        self.conn.commit()

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

    @locked(lock)
    def create_index(self, tablename, colname, indexname):
        check = "select * from sqlite_master where type='index'and tbl_name='%s'"\
        %tablename
        self.cursor.execute(check)
        results = self.cursor.fetchall()
        if results != []:
            if indexname in results[0]:
                return
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
