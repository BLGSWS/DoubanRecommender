#coding:utf-8

import os
import sys
import Queue

class UrlFix(object):

    def __init__(self):
        self.film_list = Queue.Queue()

    @classmethod
    def creat_film_ref(cls, film_id, count=0):
        '''
        count:for which page you are getting
        '''
        film_ref = '''
        https://movie.douban.com/subject/%s/comments?start=%d&limit=20&sort=new_score&status=P
        '''%(film_id, count)
        return film_ref

    def creat_flim_list(self, film_id, num):
        '''
        num:how many pages you want to get
        '''
        for i in range(num):
            count = i*20
            film_ref = self.creat_film_ref(film_id, count)
            self.film_list.put(film_ref)
        return self.film_list

    @classmethod
    def creat_first_preferbookpage(cls, uid):
        url = '''
        https://book.douban.com/people/%s/collect?sort=rating&start=0&mode=list&tags_sort=count
        '''%uid
        return url

    @classmethod
    def creat_first_preferfilmpage(cls, uid):
        url = '''
        https://movie.douban.com/people/%s/collect?start=0&sort=rating&rating=all&filter=all&mode=list
        '''%uid
        return url

    @classmethod
    def creat_filmpage_forehead(cls, film_id):
        url = 'https://movie.douban.com/subject/%s/comments'%film_id
        return url

if __name__ == '__main__':
    UFX = UrlFix()
    LIST = UFX.creat_flim_list("123", 5)
    for _ in xrange(5):
        print LIST.get()
