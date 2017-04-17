#coding:utf-8

import numpy as np
import matplotlib.pyplot as plt
import math

def sigmoid(x):
    y = 1.0/(1.0+math.e**(-x))
    return y

def get_avg_error():
    errors = []
    with file("src/bpnetwork/Logging/log.txt") as myfile:
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

    def __init__(self):
        self.book_info = []
        self.avg_results = []
        self.project_results = []
        self.res_x = None
        self.res_y = None
        self.avg_x = None
        self.avg_y = None
        self.fun = None

    def get_res_value(self, filename):
        rank_points = []
        values = []
        i = 0
        myfile = open(filename, "r")
        while True:
            line = myfile.readline()
            if not line:
                break
            if line[0] != "#":
                rank_points.append(float(i))
                value = line.split(";")
                values.append(float(value[-1]))
                self.book_info.append([value[0], value[-2], value[-1]])
                i += 1
        self.res_x = np.array(rank_points)
        self.res_y = np.array(values)

    def avg_value_regress(self):
        rank_points = []
        values = []
        i = 0
        myfile = open("src/bpnetwork/Logging/avg_res.txt", "r")
        while True:
            line = myfile.readline()
            if not line:
                break
            if line[0] != "#":
                rank_points.append(float(i))
                value = line.split(";")
                values.append(float(value[-1]))
                self.avg_results.append(value[-2])
                i += 1
        self.avg_x = np.array(rank_points)
        self.avg_y = np.array(values)
        reg_y = self.avg_y+np.ones(self.avg_y.shape[0])*0.020#y轴上调整拟合函数，方便最后统计
        cof = np.polyfit(self.avg_x, reg_y, 6)
        self.fun = np.poly1d(cof)

    def merge(self):
        step = float(self.avg_x.shape[0])/float(self.res_x.shape[0])
        for book in self.book_info:
            try:
                i = self.avg_results.index(book[1])
            except ValueError as error:
                self.project_results.append(0.610)
                continue
            y = self.fun(i*step)
            self.project_results.append(y)

    def last_result(self, n):
        error = self.res_y-np.array(self.project_results)
        discts = []
        for i in xrange(error.shape[0]):
            discts.append([self.book_info[i][0], self.book_info[i][1], error[i]])
        for i in xrange(n):
            maxvalue = 0.0
            maxposition = 0
            for j in xrange(i, len(discts)):
                if discts[j][2] > maxvalue:
                    maxposition = j
                    maxvalue = discts[j][2]
            discts[maxposition], discts[i] = discts[i], discts[maxposition]
        for i in xrange(n):
            print discts[i][0].decode("utf-8"),discts[i][1],discts[i][2]

    def plot_show(self):
        lenth = len(self.project_results)
        plt.plot(np.linspace(0, lenth, lenth), np.array(self.project_results), "ob")
        plt.plot(self.res_x, self.res_y, "og")
        #plt.plot(self.avg_x, self.avg_y, "or")
        #plt.plot(self.avg_x, self.fun(self.avg_x), lw=2)
        plt.show()

if __name__ == "__main__":
    '''minitor = Minitor()
    minitor.get_res_value("src/bpnetwork/Logging/res_4.txt")
    minitor.avg_value_regress()
    minitor.merge()
    minitor.last_result(20)
    minitor.plot_show()'''
    errors = get_avg_error()
    show_error(errors)



