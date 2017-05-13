#coding:utf-8
from sqldb import SqliteDataBase,MySqlDataBase

class MainInfo(object):

    def __init__(self, database):
        self._db = database
        self.fetchcur = None

    def connect_info(self):
        print "Database: MainInfo already connected to %s"%self._db.dbname

    def creat_film_value_table(self):
        sql = '''create table if not exists user_info (
            pk_pid mediumint not null auto_increment,
            id varchar(225) default null,
            uid varchar(225) default null,
            film_value int default null,
            primary key (pk_pid))'''
        self._db.create_table(sql, "user_info")

    def creat_prefer_book_table(self):
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
        self._db.create_table(sql, "prefer_book")

    def creat_prefer_film_table(self):
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
        self._db.create_table(sql, "prefer_film")

    def insert_uid(self, data):
        '''
        :summary:
        :param data:字典
        '''
        sql = u'''
        insert into user_info(uid,film_value) values ('%s',%s)
        '''%(data["uid"], data["value"])
        self._db.change_one(sql)

    def insert_prefer_book(self, data):
        '''
        :param data:字典
        '''
        sql = u'''
        insert into prefer_book(book_name,book_id,book_value,user_uid) values ('%s','%s',%s,'%s')
        '''%(data["book_name"], data["book_id"], data["book_value"], data["user_uid"])
        self._db.change_one(sql)

    def insert_prefer_film(self, data):
        '''
        :param data:字典
        '''
        sql = u'''
        insert into prefer_film(film_name,film_id,film_value,user_uid) values ('%s','%s',%s,'%s')
        '''%(data["film_name"], data["film_id"], data["film_value"], data["user_uid"])
        self._db.change_one(sql)

    def select_uid_from_film_value(self, count):
        '''
        :param count:查询第count个用户uid
        :return:uid
        '''
        sql = u"select uid from user_info where pk_pid=%d"%count
        result = self._db.select_one(sql)
        return result[0]

    def select_prefer_film(self, uid=None):
        '''
        :param uid:等于None时查询所有电影
        '''
        film_list = []
        if not uid:
            sql = "select film_id from prefer_film group by film_id"
        else:
            sql = u"select film_id from prefer_film where user_uid='%s'"%uid
        results = self._db.select_all(sql)
        for result in results:
            film_list.append(result[0])
        return film_list

    def select_prefer_book(self, uid):
        book_list = []
        sql = u"select book_id,book_value from prefer_book where user_uid='%s'"%uid
        results = self._db.select_all(sql)
        for result in results:
            book_list.append([result[0], result[1]])
        return book_list

    def get_user_count(self):
        sql = u"select count(*) from user_info"
        result = self._db.select_one(sql)
        return result[0]

    def get_uid_list(self):
        '''
        :summary:从prefer_film表中获取已爬取的用户
        '''
        sql = u"select user_uid from prefer_film group by user_uid"
        results = self._db.select_all(sql)
        uid_list = []
        for result in results:
            uid_list.append(result[0])
        return uid_list

    def select_book_name(self, book_id):
        sql = u"select book_name from book_info where book_id='%s' limit 1"%book_id
        result = self._db.select_one(sql)
        return result[0]

    def delete_table(self, table_name):
        sql = u"drop table if exists "+table_name.decode("utf-8")
        mesg = "Database: drop table %s successed"%table_name
        self._db.execute_sql(sql, mesg)

    def roll_back(self, uid):
        '''
        :summary:爬取异常时回卷数据（暂时这样写啦）
        '''
        sql1 = u"delete from prefer_book where user_uid='%s'"%uid
        sql2 = u"delete from prefer_film where user_uid='%s'"%uid
        print "roll back uid:%s"%uid
        self._db.execute_sql(sql1, "prefer_book roll back")
        self._db.execute_sql(sql2, "prefer_film roll back")

    def create_info_table(self):
        '''
        :summary:建立记录书籍信息和电影信息的表
        '''
        sql1 = '''
        create table book_info(book_id varchar(225) not null,book_name varchar(225) not null)
        '''
        sql2 = '''
        create table film_info(film_id varchar(225) not null,film_name varchar(225) not null)
        '''
        sqlite = SqliteDataBase()
        sqlite.create_table(sql1, "book_info")
        sqlite.create_table(sql2, "film_info")
        self._db.create_table(sql1, "book_info")
        self._db.create_table(sql2, "book_info")

        self.copy_data(["book_id", "book_name"], "prefer_film", "film_info")
        self.copy_data(["film_id", "film_name"], "prefer_film", "film_info")
