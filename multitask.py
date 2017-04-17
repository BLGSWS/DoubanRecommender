#coding:utf-8

from threading import Thread
from multiprocessing import Process
from apis import APIs

class ThreadScrapy(Thread):

    def __init__(self, api):
        Thread.__init__(self)
        self.api = api

    def run(self):
        self.api.scrapy_prefer_page()

class ThreadTrain(Thread):

    def __init__(self, api):
        Thread.__init__(self)
        self.api = api

    def run(self):
        self.api.train()


class ProcessTrain(Process):

    def __init__(self, api):
        Process.__init__(self)
        self.api = api

    def run(self):
        self.api.train()

class ProcessScrapy(Process):

    def __init__(self, api):
        Process.__init__(self)
        self.api = api

    def run(self):
        self.api.scrapy_prefer_page()
