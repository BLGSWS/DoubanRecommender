import os
import sys
import recommend
from recommend import Recmmomend, ThreadScrapy, ThreadTrain

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == '__main__':
    rd = Recmmomend()
    while(1):
        text = raw_input()
        content = text.split(" ")
        if "-getu" in content[0]:
            num = content[1]
            film_id = content[2]
            recommend.scrapy_film_value_page(id, num)
        elif "-get" in content[0]:
            rd.scrapy_prefer_page()
        elif "-train" in content[0]:
            rd.train()
        elif "-clean" in content[0]:
            cmd = content[1]
            recommend.clean_data(cmd)
        elif "-copy" in content[0]:
            recommend.copy_data()
        elif "-q" in content[0]:
            exit()
        else:
            print "no such command"
