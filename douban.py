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
    '''api = APIs()
    process_scrapy = ProcessScrapy(api)
    process_train = ProcessTrain(api)
    process_scrapy.start()
    process_train.start()'''
    #apis.scrapy_film_value_page("1292052")
    api =APIs()
    #apis.train_by_order()
    #美国队长3，金刚狼3， 钢铁侠， 奇异博士， 复仇者联盟， x-man:逆转未来
    #情书， 蓝色大门， 牯岭街， 怦然心动， 四月物语
    apis.get_results(["1292220", "1308575", "1292371", "3319755", "1292371"], "src/bpnetwork/Logging/res_4.txt")


