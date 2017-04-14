﻿#coding:utf-8

import time
import random
import Queue
import threading

from spider.urltool import UrlFix as ufx
from spider.requester import Requester
from spider.solver import BFSolver as sl
import spider.proxy as Proxy
from db.sqldb import MainInfo, MyError
from bpnetwork.network import BPNetwork
import MySQLdb
'''
实例化类
'''
class APIs(object):

    def __init__(self):
        self._req = Requester("src/spider/Cookie/Cookie0.txt")
        self._db = MainInfo()
        self._net = BPNetwork()

        self.first_film_content = None
        self.first_book_content = None

        #待训练样本缓冲区
        self.uid_queue = Queue.Queue(5)
        self.error_ample = Queue.Queue()

        #线程控制
        self.is_finish = False
        self.pause = threading.Event()
        self.pause.set()
        self.select_lock = threading.Lock()

    def scrapy_prefer_page(self):
        self.select_lock.acquire()
        self._db.creat_prefer_film_table()
        self._db.creat_prefer_book_table()
        self.select_lock.release()
        count = self._db.get_user_count()
        i = 100
        while i < count:
            self.pause.wait()
            try:
                self.select_lock.acquire()
                uid = self._db.select_uid_from_film_value(i)
                self.select_lock.release()
                print "scarpy: "+uid+" begin"
                flag = self.skip_or_not(uid)
                if flag == 0:
                    print "scarpy: uid:%s,count%d skip!"%(uid, i)
                    i += 1
                    time.sleep(random.uniform(1.5, 2))
                    continue
                self.__scrapy_prefer_film_page(uid)
                self.__scrapy_prefer_book_page(uid)
                print "scrapy: "+uid+"  success! (%d/%d)"%(i, count)
                self.uid_queue.put(uid)
                time.sleep(random.uniform(1.5, 2))
                i += 1
            except MySQLdb.OperationalError as error:
                if error[0] == 2013:
                    self._db.reconnect_database()
                    self._db.roll_back(uid)
                print self.pause
                continue
            except:
                print "scrapy: fasle uid:%s,count:%d"%(uid, i)
                self._db.roll_back(uid)
                time.sleep(10)
        self.is_finish = True

    def __scrapy_prefer_book_page(self, uid):
        self.select_lock.acquire()
        nextpage = sl.perfer_book_page_detial\
        (self.first_book_content, uid, self._db.insert_prefer_book)
        self.select_lock.release()
        while nextpage != "finish":
            self.select_lock.acquire()
            content = self._req.get_page_with_header(nextpage)
            nextpage = sl.perfer_book_page_detial(content, uid, self._db.insert_prefer_book)
            self.select_lock.release()
            time.sleep(random.uniform(1.5, 2))
        return nextpage

    def __scrapy_prefer_film_page(self, uid):
        self.select_lock.acquire()
        nextpage = sl.perfer_film_page_detial\
        (self.first_film_content, uid, self._db.insert_prefer_film)
        self.select_lock.release()
        while nextpage != "finish":
            self.select_lock.acquire()
            content = self._req.get_page_with_header(nextpage)
            nextpage = sl.perfer_film_page_detial(content, uid, self._db.insert_prefer_film)
            self.select_lock.release()
            time.sleep(random.uniform(1.5, 2))
        return nextpage

    def skip_or_not(self, uid):
        '''
        判断是否跳过用户
        :param uid:用户uid
        :return:
        '''
        film_page = ufx.creat_first_preferfilmpage(uid)
        book_page = ufx.creat_first_preferbookpage(uid)
        self.first_film_content = self._req.get_page_with_header(film_page)
        time.sleep(random.uniform(1.5, 2))
        self.first_book_content = self._req.get_page_with_header(book_page)
        time.sleep(random.uniform(1.5, 2))
        film_flag = sl.skip_or_not(self.first_film_content, 3500, 0)
        book_flag = sl.skip_or_not(self.first_book_content, 3000, 20)
        flag = film_flag*book_flag
        return flag

    def train(self):
        '''训练'''
        while not self.is_finish:
            self.pause.wait()
            if not self.error_ample.empty():
                uid = self.error_ample.get()
            else:
                uid = self.uid_queue.get()
            print "tarin: %s begin "%uid
            try:
                self.select_lock.acquire()
                film_list = self._db.select_prefer_film(uid)
                book_list = self._db.select_prefer_book(uid)
                self.select_lock.release()
                self._net.train(uid, film_list, book_list)
            except MySQLdb.OperationalError as error:
                if error[0] == 2006:
                    self._db.reconnect_database()
                    self.error_ample.put(uid)
                else:
                    raise
            except:
                self.pause.clear()
                print "locked"
            else:
                print "train: %s end"%uid

def scrapy_film_value_page(film_id):
    '''
    从电影短评区取得用户列表,尽量选择大家都看过的电影
    :param film_id:电影id
    '''
    #建表
    _db = MainInfo()
    _db.creat_film_value_table()

    _req = Requester("src/spider/Cookie/Cookie1.txt")

    #抓取第一页
    forehead = ufx.creat_filmpage_forehead(film_id)
    first_page = ufx.creat_film_ref(film_id)
    content = _req.get_page_with_header(first_page)
    num = sl.get_active(content)
    print "total values:"+num
    count = int(num)/20

    #抓取后续页
    page = forehead+sl.film_value_page_detial(content, _db.insert_uid)
    i = 1
    while i < count:
        try:
            content = _req.get_film_value_page(page)
            next_page = sl.film_value_page_detial(content, _db.insert_uid)
            print page+" success! (%d/%d)"%(i, count)
        except Exception:
        #异常处理
            time.sleep(random.uniform(10, 14))
            print "loop times: "+str(i)
            raise
        else:
            page = forehead+next_page
            time.sleep(random.uniform(2, 4))#每分钟40以下次请求
            i += 1

def train_by_order():
    _net = BPNetwork()
    _db = MainInfo()
    uid_list = _db.get_uid_list()
    for i in xrange(50, len(uid_list)):
        uid = uid_list[i]
        print uid+" begin"
        film_list = _db.select_prefer_film(uid)
        book_list = _db.select_prefer_book(uid)
        if len(film_list) != 0 and len(book_list) != 0:
            _net.train(uid, film_list, book_list)
            print uid+" end"
        else:
            print uid+" skip"

def get_results(filmids, n):
    '''
    接受一组电影，输出前n高的结果
    :param filmids:电影id（数组）
    :param n:输出前n高评价的书
    :return:
    '''
    _db = MainInfo()
    _net = BPNetwork()
    results = _net.get_results(filmids)
    books = results.items()
    for i in xrange(n):
        maxvalue = 0.0
        maxposition = 0
        for j in xrange(i, len(books)):
            if books[j][1] > maxvalue:
                maxvalue = books[j][1]
                maxposition = j
        books[maxposition], books[i] = books[i], books[maxposition]
    myfile = file("src/bpnetwork/Logging/res_1.txt", "a+")
    myfile.write("#"+str(filmids)+"\n")
    for i in xrange(n):
        book_name = _db.select_book_name(books[i][0])
        line = "%s,%s\n"%(books[i][0], books[i][1])
        myfile.write(line)

def get_avg_results():
    '''获取平均结果'''
    _db = MainInfo()
    _net = BPNetwork()
    all_films = _db.select_prefer_film()
    results = _net.get_results(all_films)
    books = results.items()
    i = 0
    limit = 1.0
    while limit > 0.6:
        maxvalue = 0.0
        maxposition = 0
        for j in xrange(i, len(books)):
            if books[j][1] > maxvalue:
                maxvalue = books[j][1]
                maxposition = j
        books[maxposition], books[i] = books[i], books[maxposition]
        limit = float(maxvalue)
        i += 1
    with file("src/bpnetwork/Logging/avg_res.txt", "a+") as myfile:
        for k in xrange(i):
            book_name = _db.select_book_name(books[k][0])
            print book_name
            myfile.write("%s,%s\n"%(books[k][0], books[k][1]))


def get_simple_results(filmids):
    _net = BPNetwork()
    _net.get_simple_results(filmids)

def keep_proxy():
    '''开启代理池'''
    Proxy.init_proxylist(False)

if __name__ == '__main__':
    get_avg_results()