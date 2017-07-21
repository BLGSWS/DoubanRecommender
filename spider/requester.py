#coding:utf-8
'''
Created on 2017年3月8日

@author: Cham
'''
import urllib2
import cookielib

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

class Requester(object):

    def __init__(self, cookiePath="spider/Cookie/Cookie0.txt"):
        self.cookie = cookielib.MozillaCookieJar(cookiePath)
        self.cookie.load(cookiePath, ignore_discard=True, ignore_expires=True)

    def get_page_with_header(self, url):
        head_user_agent = '''
        Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36(KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36
        '''
        header = {('User-Agent', head_user_agent)}
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        opener.addheaders = header
        try:
            respond = opener.open(url)
            content = respond.read()
        except urllib2.URLError as error:
            print error.code, error.reason
            raise
        opener.close()
        respond.close()
        return content

    @staticmethod
    def save_page(content, num=1):
        '''测试用'''
        print "page code type:"+str(type(content))
        i = 0
        while i < num:
            with file('spider/page/detial_page%d.html'%i, 'w') as myfile:
                myfile.write(content)
            i = i+1

if __name__ == '__main__':
    RQ = Requester()
    content = RQ.get_page_with_header("https://book.douban.com/top250")
    RQ.save_page(content)
    