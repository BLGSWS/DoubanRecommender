#coding:utf-8

import time
import random
import Queue
import threading
import ConfigParser

from spider.requester import Requester,UrlFix
from spider.solver import BFSolver as sl
from db.maininfo import MainInfo
from bpnetwork.minitor import Minitor
from bpnetwork.network import BPNetwork
import db.sqldb as sqldb

PARSER = ConfigParser.ConfigParser()
PARSER.read("db/config.cfg")
if PARSER.get("DB_Config", "database_type") == "mysql":
    from db.sqldb import MySqlDataBase as DataBase
else:
    from db.sqldb import SqliteDataBase as DataBase

class ThreadScrapy(threading.Thread):

    def __init__(self, api):
        threading.Thread.__init__(self)
        self.api = api

    def run(self):
        self.api.scrapy_prefer_page()

class ThreadTrain(threading.Thread):

    def __init__(self, api):
        threading.Thread.__init__(self)
        self.api = api

    def run(self):
        self.api.train()

class Recmmomend(object):

    def __init__(self):
        self._req = Requester("spider/Cookie/Cookie0.txt")
        database = DataBase()
        self._db = MainInfo(database)
        self._net = BPNetwork(database)
        self._net.create_tables()

        self.first_film_content = None
        self.first_book_content = None

        #待训练样本缓冲区
        self.uid_queue = Queue.Queue(5)
        self.error_ample = Queue.Queue()

        #线程控制
        self.is_finish = False
        self.pause = threading.Event()
        self.pause.set()

    def scrapy_prefer_page(self):
        self._db.creat_prefer_film_table()
        self._db.creat_prefer_book_table()
        count = self._db.get_user_count()
        i = 1
        while i < count:
            self.pause.wait()
            try:
                uid = self._db.select_uid_from_film_value(i)
                print "scarpy: %s begin"%uid
                flag = self.__skip_or_not(uid)
                if flag == 0:
                    print "scarpy: uid:%s,count%d skip!"%(uid, i)
                    i += 1
                    time.sleep(random.uniform(1.5, 2))
                    continue
                self.__scrapy_prefer_film_page(uid)
                self.__scrapy_prefer_book_page(uid)
                print "scrapy: "+uid+"  success! (%d/%d)"%(i, count)
                #self.uid_queue.put(uid)
                time.sleep(random.uniform(1.5, 2))
                i += 1
            except:
                raise
                print "scrapy: fasle uid:%s,count:%d"%(uid, i)
                self._db.roll_back(uid)
                time.sleep(10)
        while not self.error_ample.empty():
            print self.error_ample.get()
        self.is_finish = True

    def __scrapy_prefer_book_page(self, uid):
        nextpage = sl.perfer_book_page_detial\
        (self.first_book_content, uid, self._db.insert_prefer_book)
        while nextpage != "finish":
            content = self._req.get_page_with_header(nextpage)
            nextpage = sl.perfer_book_page_detial(content, uid, self._db.insert_prefer_book)
            time.sleep(random.uniform(1.5, 2))
        return nextpage

    def __scrapy_prefer_film_page(self, uid):
        nextpage = sl.perfer_film_page_detial\
        (self.first_film_content, uid, self._db.insert_prefer_film)
        while nextpage != "finish":
            content = self._req.get_page_with_header(nextpage)
            nextpage = sl.perfer_film_page_detial(content, uid, self._db.insert_prefer_film)
            time.sleep(random.uniform(1.5, 2))
        return nextpage

    def __skip_or_not(self, uid):
        '''
        判断是否跳过用户
        :param uid:用户uid
        :return:
        '''
        film_page = UrlFix.creat_first_preferfilmpage(uid)
        book_page = UrlFix.creat_first_preferbookpage(uid)
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
                film_list = self._db.select_prefer_film(uid)
                book_list = self._db.select_prefer_book(uid)
                self._net.train(uid, film_list, book_list)
            except:
                self.pause.clear()
                print "train: %s locked"%uid
            else:
                print "train: %s end"%uid

def scrapy_film_value_page(film_id, user_num):
    '''
    从电影短评区取得用户列表
    :param film_id:电影id
    '''
    #建表
    database = DataBase()
    _db = MainInfo(database)
    _db.creat_film_value_table()

    _req = Requester("spider/Cookie/Cookie1.txt")

    #抓取第一页
    forehead = UrlFix.creat_filmpage_forehead(film_id)
    first_page = UrlFix.creat_film_ref(film_id)
    content = _req.get_page_with_header(first_page)
    num = sl.get_active(content)
    if num > user_num:
        num = user_num
    print "total values:"+num
    count = int(num)/20

    #抓取后续页
    page = forehead+sl.film_value_page_detial(content, _db.insert_uid)
    i = 1
    while i < count:
        try:
            content = _req.get_page_with_header(page)
            next_page = sl.film_value_page_detial(content, _db.insert_uid)
            print page+" success! (%d/%d)"%(i, count)
        except Exception:
        #异常处理
            time.sleep(random.uniform(10, 14))
            print "error in loop times: "+str(i)
        else:
            page = forehead+next_page
            time.sleep(random.uniform(2, 4))#每分钟40以下次请求
            i += 1

def train_by_order(uid_list=None):
    '''
    从一个用户列表中取得uid进行训练
    '''
    database = DataBase()
    _net = BPNetwork(database)
    _db = MainInfo(database)
    _net.create_tables()
    if not uid_list:
        uid_list = _db.get_uid_list()
        print len(uid_list)
    for i in xrange(200, len(uid_list)):
        uid = uid_list[i]
        print uid+" begin"
        film_list = _db.select_prefer_film(uid)
        book_list = _db.select_prefer_book(uid)
        if len(film_list) != 0 and len(book_list) != 0:
            _net.train(uid, film_list, book_list)
            print uid+" end"
        else:
            print uid+" skip"

def get_outputs(filmids):
    '''
    接受一组电影，输出高于0.615分的书籍
    :param filmids:电影id（数组）
    :param filename:存储文件名
    :return:
    '''
    database = DataBase()
    _db = MainInfo(database)
    _net = BPNetwork(database)

    results = _net.get_results(filmids)
    outputs = results.items()#获取神经网络输出
    #简单选择前n项
    limit = 1.0
    i = 0
    while limit > 0.615:
        maxvalue = 0.0
        maxposition = 0
        for j in xrange(i, len(outputs)):
            if outputs[j][1] > maxvalue:
                maxvalue = outputs[j][1]
                maxposition = j
        outputs[maxposition], outputs[i] = outputs[i], outputs[maxposition]
        limit = float(maxvalue)
        i += 1
    #纪录前n项输出
    head_output = []
    for j in xrange(i):
        book_name = _db.select_book_name(outputs[j][0])
        #[book_name, book_id, book_value]
        head_output.append([book_name, outputs[j][0], outputs[j][1]])
    _mi = Minitor("avg_res.txt")
    _mi.get_output_by_array(head_output)
    results = _mi.get_results(30, 2)
    return results

def get_avg_results():
    '''
    获取平均结果
    大于0.6的平均结果按大小排序
    '''
    _database = DataBase()
    _db = MainInfo(_database)
    _net = BPNetwork(_database)

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
    with file("bpnetwork/Logging/avg_res.txt", "a+") as myfile:
        for k in xrange(i):
            book_name = _db.select_book_name(books[k][0])
            myfile.write(book_name.encode("utf-8"))
            myfile.write(";%s;%s\n"%(books[k][0], books[k][1]))

def copy_data():
    '''
    :summary:从mysql复制数据到sqlite
    '''
    db = DataBase()
    network = BPNetwork(db)
    network.create_tables()
    #network.clean_tables()

    sqldb.copy_data(["fromid", "toid", "strength"], "filmtohiddens", "filmtohiddens")
    sqldb.copy_data(["fromid", "toid", "strength"], "hiddentobook", "hiddentobook")
    sqldb.copy_data(["uid"], "hiddennode", "hiddennode")
    sqldb.copy_data(["nodeid", "strength"], "hiddenthresholds", "hiddenthresholds")
    sqldb.copy_data(["nodeid", "strength"], "bookthresholds", "bookthresholds")
    print "Database: copy data success!"

def clean_data(cmd):
    db = DataBase()
    nn_tables = ["filmtohiddens", "hiddentobook", "hiddenthresholds", "bookthresholds"]
    data_tables = ["prefer_film", "prefer_book", "user_info"]
    if cmd == "train":
        db.clean_tables(nn_tables)
    elif cmd == "data":
        db.clean_tables(data_tables)

if __name__ == '__main__':
    copy_data()
