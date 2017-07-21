#coding:utf-8

import os
import sys
import recommend
from recommend import Recmmomend, ThreadScrapy, ThreadTrain

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == '__main__':
    results = []
    while(1):
        text = raw_input()
        content = text.split(" ")
        if "-r" in content[0]:
            num = content[1]
            film_list = content[-1].split(",")
            results = recommend.get_outputs(film_list)
            for i in xrange(1, int(num)):
                print results[i][0], results[i][1], results[i][2]
        elif "-q" in content[0]:
            exit()
        elif "-log" in content[0]:
            filename = content[1]
            with file(filename, "w") as myfile:
                for result in results:
                    myfile.write(result[0].encode("utf-8"))
                    myfile.write(";%s;%s\n"%(result[1], result[2]))
        else:
            print "no such command"


