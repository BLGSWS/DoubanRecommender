#coding:utf-8

import os
import sys
import apis
from apis import APIs
#from mutiltask import ProcessScrapy, ProcessTrain
from multitask import ThreadScrapy, ThreadTrain

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == '__main__':
    '''api = APIs()
    thread_scrapy = ThreadScrapy(api)
    thread_train = ThreadTrain(api)
    thread_scrapy.start()
    thread_train.start()
    thread_scrapy.join()
    thread_train.join()'''
    #api = APIs()
    #api.scrapy_prefer_page()
    #apis.scrapy_film_value_page("1292052")
    #apis.train_by_order()
    #apis.train_by_order()
    #美国队长3，金刚狼3， 钢铁侠， 奇异博士， 复仇者联盟， x-man:逆转未来
    #情书， 蓝色大门， 牯岭街， 怦然心动， 四月物语
    with file("info.txt", "r") as myfile:
        while True:
            films = myfile.readline()
            if films[0] != "#":
                break
        film_list = films.split(",")
    results = apis.get_outputs(film_list, filename="res_6.txt")
    with file("info.txt", "a+") as myfile:
        myfile.write("/n")
        for result in results:
            info = u"%s,%s,%s\n"%(result[0], result[1], result[2])
            myfile.write(info.encode("utf-8"))
    os.system("pause")


