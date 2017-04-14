#coding:utf-8

import numpy as np
import matplotlib.pyplot as plt

def get_ave_error():
    errors = []
    with file("src/bpnetwork/Logging/log.txt") as myfile:
        while True:
            line = myfile.readline()
            if not line:
                break
            if line[0] != "#":
                error = line.split(",")
                errors.append(error[0])
    return errors

def show_error(errors):
    aves = []
    total = 0.0
    for i in xrange(len(errors)):
        total += float(errors[i])
        ave = total/(i+1)
        aves.append(ave)
    x = np.linspace(0, len(aves), len(aves))
    y = np.array(aves)
    plt.plot(x, y, 'o', x, y, lw=2)
    plt.show()

errors = get_ave_error()
show_error(errors)



