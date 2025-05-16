#!/usr/bin/env python3
import sys
import numpy as np

n, p, r, d = None, None, None, None
best_feas = None

class Node:
    def __init__(self, tsk: list, c, V: list):
        self.tsk = tsk
        self.V = V
        self.c = c

    def get_children(self):
        children = []
        for vn in self.V:
            prune = False
            b = self.V.copy()
            b.remove(vn)
            ltsk = self.tsk + [vn]
            lc = 0
            for t in ltsk:
                if r[t] <= lc:
                    lc += p[t]
                else:
                    lc += p[t] + r[t]-lc
            for j in b:
                g = max(lc, r[j])
                if g + p[j] > d[j]:
                    prune = True
                    break
            if prune:
                continue
            #PRAVIDLO 2:
            UB = 0

            if best_feas is None and b != []:
                LB = max(lc, min([r[j] for j in b])) + sum([p[j] for j in b])
                UB = max([d[j] for j in b])
                if LB > UB:
                    prune = True
            elif best_feas is not None and b != []:
                LB = max(lc, min([r[j] for j in b])) + sum([p[j] for j in b])
                UB = best_feas
                if LB >= UB:
                    prune = True


            if not prune:
                children.append(Node(ltsk, lc, b))
        return children

    def __str__(self):
        return str(self.tsk) +" -- c: " + str(self.c) + " -- V: " + str(self.V)

if __name__ == '__main__':

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

    tasks = list(range(n))

    first = Node([], 0, tasks)
    nodes = first.get_children()
    best_node = None
    while True:
        #print("=================")
        #for i in nodes:
            #print(i)
        if nodes == []:
            #print("infeseable")
            break
        nod = nodes.pop(-1)
        if nod.V == []:
            #print("Found!!")
            #print(nod)
            if best_feas is None:
                best_feas = nod.c
                best_node = nod
            elif nod.c < best_feas:
                best_feas = nod.c
                best_node = nod
        else:
            if nod.c <= min(r[j] for j in nod.V):
                nodes = nod.get_children()
            else:
                nodes = nodes + nod.get_children()



    if best_node is None:
        #print("infeseable")
        with open(sys.argv[2], "w") as f:
            f.write("-1")
    else:
        starts = [0]*n
        time = 0
        for t in best_node.tsk:
            starts[t] = max(time,r[t])
            time = max(time, r[t]) + p[t]
        #print(starts)
        with open(sys.argv[2], "w") as f:
            for s in starts:
                f.write(str(s)+"\n")
