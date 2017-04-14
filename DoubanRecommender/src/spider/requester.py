#coding:utf-8
'''
Created on 2017年3月8日

@author: Cham
'''
import urllib2
import cookielib

class Requester(object):

    def __init__(self, cookiePath="src/spider/Cookie/Cookie0.txt"):
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

    def get_film_value_page(self, url):
        head_user_agent = '''
        Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36(KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36
        '''
        header = {('User-Agent', head_user_agent),
                  ('Referer', url),
                  ('Host', "movie.douban.com"),
                  ('Accept', '''
                  #text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
                  #'''),
                  ('Cache-Control', "max-age=0"),
                  ('Connection', "keep-alive"),
                  ('Upgrade-Insecure-Requests', "1"),
                  ('Accept-Language', "zh-CN,zh;q=0.8,en;q=0.6")}
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
            with file('src/spider/page/detial_page%d.html'%i, 'w') as myfile:
                myfile.write(content)
            i = i+1

if __name__ == '__main__':
    RQ = Requester()
    content = RQ.get_page_with_header("https://book.douban.com/top250")
    RQ.save_page(content)
    