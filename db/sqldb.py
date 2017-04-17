#coding:utf-8

import ConfigParser
from warnings import filterwarnings
import MySQLdb

filterwarnings('error', category = MySQLdb.Warning)

class MyError(Exception):

    def __init__(self, uid, sql):
        Exception.__init__(self)
        self.uid = uid
        self.sql = sql

class DataBase(object):

    def __init__(self):
        '''utf-8编码'''
        self.parser = ConfigParser.ConfigParser()
        self.parser.read("src/db/config.cfg")
        self.dbname = self.parser.get("DB_Config", "database_name")
        self.conn = self.create_conn()
        self.cursor = self.conn.cursor()
        self.creat_database()
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
        self.connect_info()

    def reconnect_database(self):
        self.conn = self.create_conn()
        self.cursor = self.conn.cursor()
        self.cursor.execute("use %s"%self.dbname)
        print "Database: reconnect success!"

    def creat_database(self):
        try:
            sql = "create database if not exists %s character set utf8"%self.dbname
            self.cursor.execute(sql)
            print "Database: creat database %s successed!"%self.dbname
        except MySQLdb.Warning, e:
            print "Database: %s exists"%self.dbname

    def connect_info(self):
        pass

class MainInfo(DataBase):

    def __init__(self):
        DataBase.__init__(self)
        self.fetchcur = None

    def connect_info(self):
        print "Database: MainInfo already connected to %s"%self.dbname

    def creat_film_value_table(self):
        try:
            sql = '''create table if not exists user_info (
                pk_pid mediumint not null auto_increment,
                id varchar(225) default null,
                uid varchar(225) default null,
                film_value int default null,
                primary key (pk_pid))'''
            self.cursor.execute(sql)
            print "DataBase: create table user_info succeeded!"
        except MySQLdb.Warning, e:
            print e

    def creat_prefer_book_table(self):
        try:
            sql = '''create table if not exists prefer_book(
                pk_pid mediumint not null auto_increment,
                book_id varchar(225) default null,
                book_name varchar(1023) default null,
                user_id varchar(225) default null,
                user_uid varchar(225) default null,
                book_value int default null,
                book_score float default null,
                value_people int default null,
                index(user_uid),
                primary key (pk_pid))'''
            self.cursor.execute(sql)
            print "DataBase: create table prefer_book succeeded!"
        except  MySQLdb.Warning, e:
            print e

    def creat_prefer_film_table(self):
        try:
            sql = '''create table if not exists prefer_film(
                pk_pid mediumint not null auto_increment,
                film_id varchar(225) default null,
                film_name varchar(1023) default null,
                user_id varchar(225) default null,
                user_uid varchar(225) default null,
                film_value int default null,
                film_score float default null,
                value_people int default null,
                index(user_uid),
                primary key (pk_pid))'''
            self.cursor.execute(sql)
            print "DataBase: create table prefer_film succeeded!"
        except  MySQLdb.Warning, e:
            print e

    def insert_uid(self, data):
        '''
        :param data:字典
        '''        
        sql = u'''
        insert into user_info(uid,film_value) values ('%s',%s)
        '''%(data["uid"], data["value"])
        self.cursor.execute(sql)
        self.conn.commit()

    def insert_prefer_book(self, data):
        '''
        :param data:字典
        '''
        #print u"%s,%s"%(data["book_name"],data["book_value"])
        sql = u'''
        insert into prefer_book(book_name,book_id,book_value,user_uid) values ('%s','%s',%s,'%s')
        '''%(data["book_name"], data["book_id"], data["book_value"], data["user_uid"])
        self.cursor.execute(sql)
        self.conn.commit()

    def insert_prefer_film(self, data):
        '''
        :param data:字典
        '''
        #print u"%s,%s"%(data["film_name"],data["film_value"])
        sql = u'''
        insert into prefer_film(film_name,film_id,film_value,user_uid) values ('%s','%s',%s,'%s')
        '''%(data["film_name"], data["film_id"], data["film_value"], data["user_uid"])
        self.cursor.execute(sql)
        self.conn.commit()

    def select_uid_from_film_value(self, count):
        sql = u"select uid from user_info where pk_pid=%d"%count
        self.cursor.execute(sql)
        res = self.cursor.fetchone()
        return res[0]

    def select_prefer_film(self, uid=None):
        '''
        :param uid:等于None时查询所有电影
        '''
        film_list = []
        if not uid:
            sql = "select film_id from prefer_film group by film_id"
        else:
            sql = u"select film_id from prefer_film where user_uid='%s'"%uid
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if not results:
            raise MyError(uid, sql)
        for result in results:
            film_list.append(result[0])
        return film_list

    def select_prefer_book(self, uid):
        book_list = []
        sql = u"select book_id,book_value from prefer_book where user_uid='%s'"%uid
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if not results:
            raise MyError(uid, sql)
        for result in results:
            book_list.append([result[0], result[1]])
        return book_list

    def get_user_count(self):
        sql = u"select count(*) from user_info"
        self.cursor.execute(sql)
        num = self.cursor.fetchone()
        return num[0]

    def get_uid_list(self):
        sql = u"select user_uid from prefer_film group by user_uid"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        uid_list = []
        for result in results:
            uid_list.append(result[0])
        return uid_list

    def select_book_name(self, book_id):
        sql = u"select book_name from prefer_book where book_id='%s' limit 1"%book_id
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result[0]

    def delete_table(self, table_name):
        sql = u"drop table if exists "+table_name.decode("utf-8")
        print "Database: drop table %s successed"%table_name
        self.cursor.execute(sql)

    def roll_back(self, uid):
        sql1 = u"delete from prefer_book where user_uid='%s'"%uid
        sql2 = u"delete from prefer_film where user_uid='%s'"%uid
        self.cursor.execute(sql1)
        self.cursor.execute(sql2)
        self.conn.commit()
        print "roll back uid:%s"%uid

def delete_tables():
    _db = MainInfo()
    _db.delete_table("prefer_book")
    _db.delete_table("prefer_film")

if __name__ == '__main__':
    _db = MainInfo()
    uid_list = _db.get_uid_list()
    print uid_list