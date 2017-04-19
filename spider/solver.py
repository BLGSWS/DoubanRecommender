#coding:utf-8

import re
from bs4 import BeautifulSoup

def set_value(str_value):
    if str_value == u"很差":
        return u'1'
    if str_value == u"较差":
        return u'2'
    if str_value == u"还行":
        return u'3'
    if str_value == u"推荐":
        return u'4'
    if str_value == u"力荐":
        return u'5'
    return u'0'

class BFSolver(object):
    '''
    工具类:基于BeautifulSoup的解析器
    '''

    def __init__(self):
        pass

    @classmethod
    def get_active(cls, content):
        '''
        :param content:html文档
        :return:评价过电影的人数
        '''
        soup = BeautifulSoup(content, "html.parser")
        total = soup.find("li", class_="is-active").find("span").string
        num = total.replace(u"看过(", u"").replace(u")", u"")
        return num

    @classmethod
    def skip_or_not(cls, content, max_num, min_num):
        '''
        判断是否跳过此用户
        :param content:html文档
        :param max_num:可接受的最大电影数/书籍数
        :param min_num:可接受的最小电影数/书籍数
        '''
        soup = BeautifulSoup(content, "html.parser")
        num_str = soup.find("div", id="wrapper").find("div", class_="info").find("h1").string
        num = re.search(ur"\([0-9]+\)", num_str).group().replace(u"(", u"").replace(u")", u"")
        if int(num) <= min_num or int(num) >= max_num:
            return 0
        else:
            return 1

    @classmethod
    def film_value_page_detial(cls, content, save):
        '''
        id:用户id
        value:对电影的评价
        '''
        soup = BeautifulSoup(content, "html.parser")
        comments = soup.find_all("div", class_="comment-item")
        for comment in comments:
            #avatar=comment.find("div",class_="avatar")
            #img=avatar.find("img").get("src")
            info = comment.find("span", class_="comment-info")
            href = info.find("a").get("href")
            usr_id = href.replace(u"https://www.douban.com/people/", u"").replace(u"/", u"")
            try:
                str_value = info.find("span", class_=re.compile(r"allstar[\s\S]*")).get("title")
            except AttributeError:
                str_value = 0
            value = set_value(str_value)
            data = {"uid":usr_id, "value":value}
            save(data)
        next_page = soup.find("a", class_="next").get("href")
        return str(next_page)

    @classmethod
    def perfer_book_page_detial(cls, content, uid, save):
        '''
        :param content:html文档
        :param uid:用户uid
        :param save:回调函数
        '''
        soup = BeautifulSoup(content, "html.parser")
        li_list = soup.find("ul", class_="list-view")
        lists = li_list.find_all("li")
        for elm in lists:
            title = elm.find("div", class_="title")
            book_name_u = title.find("a").string
            book_href = title.find("a").get("href")
            book_id = book_href.replace(u"https://book.douban.com/subject/", u"").replace(u"/", u"")
            date = elm.find("div", class_="date")
            try:
                str_value = date.find("span").get("class")
                value = str_value[0].replace(u"rating", u"").replace(u"-t", u"")
            except AttributeError:
                #找不到星星
                return "finish"
            book_name = book_name_u.rstrip(u" ").strip(u"\n").lstrip(u" ").replace(u"'", u"")
            #book_name:书名;book_id:书编号;book_value:对书的评价
            data = {"book_name":book_name, "book_id":book_id, "book_value":value, "user_uid":uid}
            save(data)
        try:
            next_page = soup.find("span", class_="next").find("a").get("href")
        except AttributeError:
            #找不到下一页按钮
            return "finish"
        return str(next_page)

    @classmethod
    def perfer_film_page_detial(cls, content, uid, save):
        '''
         :param content:html文档
        :param uid:用户uid
        :param save:回调函数
        '''
        soup = BeautifulSoup(content, "html.parser")
        li_list = soup.find("ul", class_="list-view")
        lists = li_list.find_all("li")
        for elm in lists:
            title = elm.find("div", class_="title")
            film_name_u = title.find("a").string
            film_href = title.find("a").get("href")
            film_id = film_href.replace\
            (ur"https://movie.douban.com/subject/", u"").replace(u"/", u"")
            date = elm.find("div", class_="date")
            try:
                str_value = date.find("span").get("class")
            except AttributeError:
                #如果此人所有电影都给了4星或者5星
                return "finish"
            value = str_value[0].replace(u"rating", u"").replace(u"-t", u"")
            if int(value) < 5:
                #暂时不抓取评价小于五星的电影
                return "finish"
            film_name = film_name_u.rstrip(u" ").strip(u"\n").lstrip(u" ").replace(u"'", u"")
            #film_name:影片名，film_id:影片编号，film_value:对影片的评价
            data = {"film_name":film_name, "film_id":film_id, "film_value":value, "user_uid":uid}
            save(data)
        try:
            next_page = soup.find("span", class_="next").find("a").get("href")
        except AttributeError:
            #找不到下一页按钮
            return "finish"
        return str(next_page)

if __name__ == '__main__':
    pass