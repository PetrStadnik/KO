#!/usr/bin/env python3
import sys
import numpy as np


if __name__ == '__main__':
    n, p, r, d = None, None, None, None
    count = 0
    file = open(sys.argv[1], "r")
    for line in file:
        if count == 0:
            n = int(line.rstrip())
            p = n * [0]
            r = n * [0]
            d = n * [0]
        else:
            hwl = list(map(int, line.rstrip().split(" ")))
            p[count - 1] = hwl[0]
            r[count - 1] = hwl[1]
            d[count - 1] = hwl[2]
        count += 1

    print(p, r, d)
    INF = 999999999
