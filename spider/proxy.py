#coding:utf-8
'''
从http://www.xicidaili.com/nn/网站获取代理
'''
import time
import random
import urllib2
import requests
from bs4 import BeautifulSoup

class ProxyPool(object):

    def __init__(self):
        global proxy_array
        proxy_array = []

    def get_proxy(self, url):
        head_user_agent = '''
        Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36
        '''
        header = {('User-Agent', head_user_agent)}
        opener = urllib2.build_opener()
        opener.addheaders = header
        try:
            respond = opener.open(url)
        except urllib2.URLError, error:
            if hasattr(error, "code"):
                print error.code
            if hasattr(error, "reason"):
                print error.reason
            return
        else:
            content = respond.read()
            opener.close()
            respond.close()
            try:
                self.slover(content)
            except:
                return

    def slover(self, content):
        soup = BeautifulSoup(content, "html.parser")
        ip_list = soup.find("table", id="ip_list")
        ipaddrs = ip_list.find_all("tr")
        del ipaddrs[0], ipaddrs[-1]
        for ipaddr in ipaddrs:
            tds = ipaddr.find_all("td")
            address = tds[1].string
            port = tds[2].string
            speed = tds[6].find("div", class_="bar").get("title").replace(u"秒", u"")
            connect_time = tds[7].find("div", class_="bar").get("title").replace(u"秒", u"")
            days = tds[8].string
            if float(speed) < 1 and float(connect_time) < 1 and days.find(u"分钟") == -1:
                proxy = str(address)+":"+str(port)
                proxy_array.append(proxy)

    def init_proxylist_by_test(self):
        myfile = open("Case/proxy.txt")
        while True:
            line = myfile.readline()
            if not line:
                break
            else:
                proxy_array.append(str(line))

def init_proxylist(flag):
    '''
    :param flag:引入并发执行True，否则False
    '''
    pool = ProxyPool()
    if not flag:
        pool.get_proxy('http://www.xicidaili.com/nn/')
        print "got proxy list!"
        return
    else:
        while True:
            pool.get_proxy('http://www.xicidaili.com/nn/')
            time.sleep(random.uniform(20, 40))

def test_proxy():
    '''测试代理是否可用'''
    url = 'http://lwons.com/wx'
    for p in proxy_array:
        proxy = {"http":"http://"+p}
        try:
            res = requests.get(url, proxies=proxy, timeout=5)
            if res.text == "default":
                print p+"  success!"
            else:
                print" false!"
        except:
            raise
            #print p+" error!"

def get_proxy():
    '''获取一个代理'''
    if len(proxy_array) == 0:
        print "you forgot INIT,no address in list"
        return None
    proxy = random.choice(proxy_array)
    return str(proxy)
    