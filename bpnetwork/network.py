#coding:utf-8
from warnings import filterwarnings
import math
import MySQLdb
import numpy as np

import sys

from db.sqldb import DataBase

filterwarnings('error', category = MySQLdb.Warning)

def sigmoid(x):
    if isinstance(x, np.ndarray):
        x = x.getA()
    y = 1.0/(1.0+math.e**(-x))
    return y

def inner_dot(x, y):
    m = np.dot(x.T, y)
    inner = np.mat(np.diag(m))
    return inner

def layer_to_table(layer):
    if layer == 0:
        table = "filmtohidden"
    elif layer == 1:
        table = "hiddentobook"
    return table

def layer_to_threshold(layer):
    if layer == 0:
        table = "hiddenthreshold"
    if layer == 1:
        table = "bookthreshold"
    return table

class BPNetwork(DataBase):

    def __init__(self):
        DataBase.__init__(self)
        try:
            self.__creat_tables()
        except MySQLdb.Warning as e:
            print "Database: tables of bpnetwork already existed"

        self.uid = None
        self.step = None#下降步长

        self.film_hidden_matrix = np.array([[]])#输入层至隐藏层连接强度
        self.hidden_book_matrix = np.array([[]])#隐藏层至输出层连接强度

        self.film_output = np.array([])#输入
        self.hidden_output = np.array([])#隐藏层输出
        self.book_output = np.array([])#输出层输出

        self.hidden_node = []#隐藏层节点

        self.hidden_threshold = np.array([])#隐藏层阈值
        self.book_threshold = np.array([])#输出层阈值

        #本轮训练不更新的连接
        self.hidden_book_zeros = {}
        self.film_hidden_zeros = {}

    def connect_info(self):
        print "Database: BPNetwork already connected to %s"%self.dbname

    def __creat_tables(self):
        self.cursor.execute('''
        create table if not exists hiddennode(pk_pid mediumint not null auto_increment,uid varchar(225) not null,primary key (pk_pid))
        ''')
        self.cursor.execute('''
        create table if not exists filmtohidden(fromid varchar(225) not null,toid varchar(225) not null,strength float not null,index(toid))
        ''')
        self.cursor.execute('''
        create table if not exists hiddentobook(fromid varchar(225) not null,toid varchar(225) not null,strength float not null,index(fromid))
        ''')
        self.cursor.execute('''
        create table if not exists hiddenthreshold(nodeid varchar(225) not null,strength float not null)
        ''')
        self.cursor.execute('''
        create table if not exists bookthreshold(nodeid varchar(225) not null,strength float not null)
        ''')
        print "Database: create network's tables success"

    def clean_tables(self):
        '''测试用'''
        try:
            self.cursor.execute("drop table if exists hiddennode")
            self.cursor.execute("drop table if exists filmtohidden")
            self.cursor.execute("drop table if exists hiddentobook")
            self.cursor.execute("drop table if exists hiddenthreshold")
            self.cursor.execute("drop table if exists bookthreshold")
        except MySQLdb.Warning:
            pass
        print "DataBase: clean tables success"

    def select_from_table(self, layer):
        '''测试用'''
        tablename = layer_to_table(layer)
        self.cursor.execute("select * from %s"%tablename)
        results = self.cursor.fetchall()
        for result in results:
            print result

    def get_matrix_strength(self, fromid, toid, layer):
        '''获得矩阵权重'''
        table = layer_to_table(layer)
        self.cursor.execute("select strength from %s where fromid='%s' and toid='%s'"\
        %(table, fromid, toid))
        res = self.cursor.fetchone()
        if not res:
            if layer == 0:
                self.film_hidden_zeros[fromid+toid] = 1
                return -0.2
            if layer == 1:
                self.hidden_book_zeros[toid+fromid] = 1
                return 0.0
            #重要参数-->未加入矩阵链接权值
        else:
            return res[0]

    def get_threshold_strength(self, nodeids, layer):
        '''获得某层阈值权重
           layer = 0：隐藏层阈值
           layer = 1：输出层阈值'''
        table = layer_to_threshold(layer)
        thetas = []
        for nodeid in nodeids:
            self.cursor.execute("select strength from %s where nodeid='%s'"%(table, nodeid))
            res = self.cursor.fetchone()
            if not res:
                #默认
                thetas.append(0.0)
            else:
                thetas.append(res[0])
        return np.array([thetas])

    def set_threshold_strength(self, nodeid, strength, layer):
        '''更新某层阈值权重
           layer = 0：隐藏层阈值
           layer = 1：输出层阈值'''
        table = layer_to_threshold(layer)
        self.cursor.execute("select strength from %s where nodeid='%s'"%(table, nodeid))
        res = self.cursor.fetchone()
        if not res:
            self.cursor.execute("insert into %s (strength,nodeid) values(%f,'%s')"\
            %(table, strength, nodeid))
        else:
            self.cursor.execute("update %s set strength=%f where nodeid='%s'"\
            %(table, strength, nodeid))

    def set_matrix_strength(self, fromid, toid, layer, strength):
        '''更新矩阵权重
           layer = 0：filmtohidden
           layer = 1：hiddentobook'''
        table = layer_to_table(layer)
        self.cursor.execute("select strength from %s where fromid='%s' and toid='%s'"\
        %(table, fromid, toid))
        res = self.cursor.fetchone()
        if not res:
            self.cursor.execute("insert into %s (strength,fromid,toid) values (%f,'%s','%s')"\
            %(table, strength, fromid, toid))
        else:
            self.cursor.execute("update %s set strength=%f where fromid='%s' and toid='%s'"\
            %(table, strength, fromid, toid))

    def generate_hiddennode(self, uid, films, books):
        '''生成隐藏节点'''
        self.cursor.execute("insert into hiddennode (uid) values ('%s')"%uid)
        self.conn.commit()
        for film in films:
            self.set_matrix_strength(film, uid, 0, 0.01)
        for book in books:
            self.set_matrix_strength(uid, book, 1, 0.01)
        #这里设为0.1的话，3星（target=0.5）评分会略微提高权值
        #重要参数-->初始权值0.01

    def get_hiddennodes(self, films, books):
        '''获得与前后层节点相关的隐藏层节点
            :param films：电影列表
            :param books：书籍列表'''
        hiddennodelist = {}
        #获取与
        for film in films:
            self.cursor.execute("select toid from filmtohidden where fromid='%s'"%film)
            results = self.cursor.fetchall()
            for result in results:
                hiddennodelist[result[0]] = 1
        for book in books:
            self.cursor.execute("select fromid from hiddentobook where toid='%s'"%book)
            results = self.cursor.fetchall()
            for result in results:
                hiddennodelist[result[0]] = 1
        return hiddennodelist.keys()

    def get_books(self, hidden_nodes):
        '''获取与隐藏层节点相关的书籍节点'''
        booknodelist = {}
        for hidden_node in hidden_nodes:
            self.cursor.execute("select toid from hiddentobook where fromid='%s'"%hidden_node)
            results = self.cursor.fetchall()
            for result in results:
                booknodelist[result[0]] = 1
        return booknodelist.keys()

    def update_network(self, films, books):
        self.hidden_node = self.get_hiddennodes(films, books)

        #获得权重矩阵w
        film_hidden_matrix = [[self.get_matrix_strength(film, hidden, 0)
                               for hidden in self.hidden_node]
                              for film in films]
        hidden_book_matrix = [[self.get_matrix_strength(hidden, book, 1)
                               for book in books]
                              for hidden in self.hidden_node]
        self.film_hidden_matrix = np.matrix(film_hidden_matrix)
        self.hidden_book_matrix = np.matrix(hidden_book_matrix)

        #获得阈值theat
        self.hidden_threshold = self.get_threshold_strength(self.hidden_node, 0)
        self.book_threshold = self.get_threshold_strength(books, 1)

        #获得当前输出结果
        self.film_output = np.ones_like(films, dtype=np.float)
        hidden_input = np.dot(self.film_output, self.film_hidden_matrix)
        self.hidden_output = sigmoid(hidden_input-self.hidden_threshold)
        book_input = np.dot(self.hidden_output, self.hidden_book_matrix)
        self.book_output = sigmoid(book_input-self.book_threshold)

        return self.book_output

    def get_filmhidden_matrix(self, films):
        '''数据量过大情况下，效率更高的矩阵建立方式'''
        hiddens = self.get_hiddennodes(films, [])
        matrix = np.ones([len(films), len(hiddens)])
        matrix = matrix*(-0.2)
        i = 0
        for film in films:
            self.cursor.execute("select toid,strength from filmtohidden where fromid='%s'"%film)
            results = self.cursor.fetchall()
            for result in results:
                j = hiddens.index(result[0])
                if j != None:
                    matrix[i, j] = result[1]
            i += 1
        return matrix

    def get_hiddenbook_matrix(self, hiddens):
        '''数据量过大情况下，效率更高的矩阵建立方式'''
        books = self.get_books(hiddens)
        matrix = np.zeros([len(hiddens), len(books)])
        i = 0
        for hidden in hiddens:
            self.cursor.execute("select toid,strength from hiddentobook where fromid='%s'"%hidden)
            results = self.cursor.fetchall()
            for result in results:
                j = books.index(result[0])
                if j != None:
                    matrix[i, j] = result[1]
            i += 1
        return matrix

    def get_results(self, films):
        '''获得预测结果,只接受一组film'''
        hiddens = self.get_hiddennodes(films, [])
        books = self.get_books(hiddens)
        #print "books:%d"%len(books)
        self.hidden_threshold = self.get_threshold_strength(hiddens, 0)
        self.book_threshold = self.get_threshold_strength(books, 1)
        self.film_hidden_matrix = self.get_filmhidden_matrix(films)
        self.hidden_book_matrix = self.get_hiddenbook_matrix(hiddens)
        self.film_output = np.array([1.0]*len(films))#
        hidden_input = np.dot(self.film_output, self.film_hidden_matrix)
        self.hidden_output = sigmoid(hidden_input-self.hidden_threshold)
        book_input = np.dot(self.hidden_output, self.hidden_book_matrix)
        self.book_output = sigmoid(book_input-self.book_threshold)
        output_dict = {}
        for i in xrange(len(books)):
            output_dict[books[i]] = self.book_output[0, i]
        return output_dict

    def back_propagate(self, origins, targets, STEP):
        '''
        前馈算法
        :param origins:输出层当前的输出
        :param targets:输出层应该的输出
        :param STEP：下降步长
        '''
        errors = targets-origins
        self.save_cost(errors)
        changes = inner_dot(origins, (np.ones_like(origins)-origins))
        book_changes = inner_dot(changes, errors)
        hidden_book_delta = np.dot(self.hidden_output.reshape(-1, 1), book_changes.reshape(1, -1))
        changes = inner_dot(self.hidden_output,\
        (np.ones_like(self.hidden_output)-self.hidden_output))
        errors = np.dot(book_changes, self.hidden_book_matrix.T)
        hidden_changes = inner_dot(changes, errors)
        film_hidden_delta = np.dot(self.film_output.reshape(-1, 1), hidden_changes.reshape(1, -1))

        self.hidden_book_matrix += hidden_book_delta*STEP
        self.book_threshold += -book_changes*STEP
        self.film_hidden_matrix += film_hidden_delta*STEP
        self.hidden_threshold += -hidden_changes*STEP

    def save_cost(self, errors):
        '''
        :summary:计算均方误差并储存
        '''
        lenth = np.shape(errors)[1]
        total = 0.0
        for i in xrange(lenth):
            total = errors[0, i]**2+total
        ave_error = total/lenth
        total = 0.0
        for i in xrange(lenth):
            total = errors[0, i]**2+total
        ms_error = total
        with file("bpnetwork/Logging/error.txt", "a+") as myfile:
            myfile.write("%f,%f,%s\n"%(ave_error, ms_error, self.uid))

    def train(self, uid, films, book_packs, STEP=0.40):
        '''
        :summary:训练并储存训练结果
        :param book_pack: [book_id, book_value]
        :param film_pack: [film_id, film_value]
        '''
        self.uid = uid
        books = []
        values = []
        for book_pack in book_packs:
            books.append(book_pack[0])
            values.append((book_pack[1]-1.0)*0.25)
        self.generate_hiddennode(uid, films, books)
        book_output = self.update_network(films, books)
        targets = np.array(values)
        self.back_propagate(book_output, targets, STEP)
        #储存
        for i in xrange(len(self.hidden_node)):
            for j in xrange(len(books)):
                if books[j]+self.hidden_node[i] in self.hidden_book_zeros:
                    continue
                self.set_matrix_strength\
                (self.hidden_node[i], books[j], 1, self.hidden_book_matrix[i, j])
            self.conn.commit()
        for i in xrange(len(films)):
            for j in xrange(len(self.hidden_node)):
                if films[i]+self.hidden_node[j] in self.film_hidden_zeros:
                    continue
                self.set_matrix_strength\
                (films[i], self.hidden_node[j], 0, self.film_hidden_matrix[i, j])
            self.conn.commit()
        for i in xrange(len(books)):
            self.set_threshold_strength(books[i], self.book_threshold[0, i], 1)
        self.conn.commit()
        for i in xrange(len(self.hidden_node)):
            self.set_threshold_strength(self.hidden_node[i], self.hidden_threshold[0, i], 0)
        self.conn.commit()

if __name__ == "__main__":
    _net = BPNetwork()
    _net.clean_tables()
    '''_net.train("xiaoming", ["1", "2", "3", "4"], [["a", 5], ["c", 4]])
    _net.train("xiaoli", ["4", "5", "6", "7"], [["a", 5], ["b", 3]])
    output = _net.get_results(["5", "6", "4"])
    print output
    _net.clean_tables()'''
    #net.train("xiaohua", ["1", "2"], [["a", 5],["c",3]])'''

    '''output = net.get_results(["1292220"])
    MAX = 0.0
    for k in output:
        if output[k] >= MAX:
            MAX = output[k]
            print "dict[%s] =" % k, output[k]'''
    #net.clean_tables()'''
    '''for i in xrange(1):
        net.train("xiaohua", ["1", "3"], [["a", 4], ["b", 2]])
        net.train("xiaozhi", ["2"], [["c", 4]])
        net.train("xiaoming", ["1", "2"], [["a", 5],["c",3]])
    output = net.get_results(["1"])
    print output'''

        