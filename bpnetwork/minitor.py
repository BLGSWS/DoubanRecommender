#coding:utf-8

import numpy as np
import matplotlib.pyplot as plt
import math

def sigmoid(x):
    y = 1.0/(1.0+math.e**(-x))
    return y

def get_avg_error():
    errors = []
    with file("bpnetwork/Logging/error.txt") as myfile:
        while True:
            line = myfile.readline()
            if not line:
                break
            if line[0] != "#":
                error = line.split(",")
                errors.append(error[0])
    return errors

def show_error(errors):
    aves = []
    total = 0.0
    for i in xrange(len(errors)):
        total += float(errors[i])
        ave = total/(i+1)
        aves.append(ave)
    x = np.linspace(0, len(aves), len(aves))
    y = np.array(aves)
    plt.plot(x, y, 'o', x, y, lw=2)
    plt.show()

class Minitor(object):

    def __init__(self, avgfilename):
        self.book_info = []#当前结果信息
        self.avg_results = []#平均结果
        self.project_values = []#平均结果在当前结果空间内的值
        self.results = []#最终结果
        self.errors = []#当前结果对平均结果误差
        self.output_x = None
        self.output_y = None
        self.avg_x = None
        self.avg_y = None
        self.fun = None#平均结果拟合后的函数
        self.__avg_value_regress("bpnetwork/Logging/"+avgfilename)

    def get_output_by_file(self, filename):
        '''
        从文件中读取神经网络输出
        :param filename:文件名
        '''
        rank = []
        values = []
        i = 0
        myfile = open("bpnetwork/Logging/"+filename, "r")
        while True:
            line = myfile.readline()
            if not line:
                break
            if line[0] != "#":
                rank.append(float(i))
                info = line.split(";")
                values.append(float(info[2]))
                self.book_info.append([info[0], info[1], info[2]])
                i += 1
        self.output_x = np.array(rank)
        self.output_y = np.array(values)

    def get_output_by_array(self, head_output):
        '''
        从数组传入神经网络输出
        :param head_output:高于0.615神经网络输出，从大到小排序
        '''
        rank = []
        values = []
        for i in xrange(len(head_output)):
            rank.append(i)
            values.append(head_output[i][-1])
        self.book_info = head_output
        self.output_x = np.array(rank)
        self.output_y = np.array(values)

    def __avg_value_regress(self, filename):
        '''
        从文件中读取平均输出
        拟合平均输出
        '''
        rank = []
        values = []
        i = 0
        myfile = open(filename, "r")
        while True:
            line = myfile.readline()
            if not line:
                break
            if line[0] != "#":
                rank.append(float(i))
                value = line.split(";")
                values.append(float(value[-1]))
                self.avg_results.append(value[-2])
                i += 1
        self.avg_x = np.array(rank)
        self.avg_y = np.array(values)
        #y轴上调整拟合函数，方便最后统计
        reg_y = self.avg_y+np.ones(self.avg_y.shape[0])*0.020
        cof = np.polyfit(self.avg_x, reg_y, 6)
        self.fun = np.poly1d(cof)

    def __merge(self):
        '''
        计算与每一个书籍的输出对应的平均输出
        '''
        projects = []
        step = float(self.avg_x.shape[0])/float(self.output_x.shape[0])
        for book in self.book_info:
            try:
                i = self.avg_results.index(book[1])
            except ValueError:
                #如果书籍在平均输出中找不到，这设置默认值0.610
                projects.append(0.610)
                continue
            reg_y = self.fun(i*step)
            projects.append(reg_y)
        self.project_values = np.array(projects)

    def get_results(self, n, count):
        '''
        取得前n项最终结果
        count越高，输出将更趋向于推荐小众书籍
        '''
        self.__merge()
        errors = self.output_y-self.project_values
        results = []
        for i in xrange(errors.shape[0]):
            revise = sigmoid((1.0-self.output_y[i])*2.5)
            errors[i] = errors[i]*(revise*2)**count
            results.append([self.book_info[i][0], self.book_info[i][1], errors[i]])
        #简单选择选择前n项
        for i in xrange(n):
            maxvalue = 0.0
            maxposition = 0
            for j in xrange(i, len(results)):
                if results[j][2] > maxvalue:
                    maxposition = j
                    maxvalue = results[j][2]
            results[maxposition], results[i] = results[i], results[maxposition]
        for i in xrange(n):
            if isinstance(results[i][0], str):
                results[i][0] = results[i][0].decode("utf-8")
            print results[i][0], results[i][1], results[i][2]
        self.errors = errors+np.ones(errors.shape[0])*0.60
        return results

    def plot_show(self):
        lenth = len(self.project_values)
        plt.plot(np.linspace(0, lenth, lenth), np.array(self.project_values), "ob")
        plt.plot(self.output_x, self.output_y, "og")
        plt.plot(self.output_x, self.errors, "or")
        #plt.plot(self.avg_x, self.avg_y, "or")
        #plt.plot(self.avg_x, self.fun(self.avg_x), lw=2)
        plt.show()

if __name__ == "__main__":
    '''mi = Minitor("avg_res.txt")
    mi.get_output_by_file("res_4.txt")
    mi.get_results(30, 4)
    mi.plot_show()'''
    a = "love"
    print type(a)
    #error = get_avg_error()
    #show_error(error)



