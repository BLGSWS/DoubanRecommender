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
    apis.get_results(["25820460", "25765735", "1432146"], 200)


