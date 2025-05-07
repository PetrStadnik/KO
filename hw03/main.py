#!/usr/bin/env python3
import sys
import gurobipy as g
import numpy as np


class Graph:
    def __init__(self, size):
        self.size = size
        self.lb = np.zeros((size, size), dtype=int)
        self.ub = np.zeros((size, size), dtype=int)
        self.flow = np.zeros((size, size), dtype=int)

    def add_edge(self, u, v, upper, lower):
        self.ub[u][v] = upper
        self.lb[u][v] = lower

    def fordFulkerson(self, source, sink):
        while True:
            path = self.bfs([source], sink)
            if path == None:
                return self.flow
            else:
                tup = path[1::2]
                _, vals = zip(*tup)
                val = min(vals)
                #print(path)
                #print(val)
                #print(self.flow)
                if(val == 0):
                    break
                while path != [sink]:
                    u = path.pop(0)
                    f = path.pop(0)[0]
                    v = path[0]
                    if f:
                        self.flow[u][v] += val
                    else:
                        self.flow[v][u] -= val

    def dfs(self, s, t, visited=[], path=[]):
        visited = visited.copy()
        path = path.copy()
        visited.append(s)
        path.append(s)
        r = None
        if s == t:
            #print(path)
            return path
        for v in range(self.size):
            if v not in visited:
                if self.flow[s][v] < self.ub[s][v] and self.ub[s][v] > 0:
                    r = self.dfs(v, t, visited, path+[(True, int(self.ub[s][v] - self.flow[s][v]))])
                    if r is not None:
                        return r
                if self.flow[v][s] > self.lb[v][s] and self.ub[v][s] > 0:
                    r = self.dfs(v, t, visited, path+[(False, int(self.flow[v][s] - self.lb[v][s]))])
                    if r is not None:
                        return r
        return r

    def bfs(self, queue, t):
        s = queue.pop(0)
        path = [s]
        visited = [s]
        pos = 0
        while s != t:
            for v in range(self.size):
                if v not in visited:
                    if self.flow[s][v] < self.ub[s][v] and self.ub[s][v] > 0:
                        queue.append((s, True, v, pos, path+[(True, int(self.ub[s][v] - self.flow[s][v])), v]))
                    if self.flow[v][s] > self.lb[v][s] and self.ub[v][s] > 0:
                        queue.append((s, False, v, pos, path+[(False, int(self.flow[v][s] - self.lb[v][s])), v]))

            if queue == []:
                return None
            st = queue.pop(0)
            path = st[4]
            s = st[2]
            if s==t:
                return path
            visited.append(s)



if __name__ == '__main__':

    C, P, cp, l, u, d = None, None, None, None, None, None
    count = 0

    file = open(sys.argv[1], "r")
    for line in file:
        if count == 0:
            C, P = list(map(int, line.rstrip().split(" ")))
            cp = C * [0]
            l = C * [0]
            u = C * [0]
        elif count < C+1:
            hwl = list(map(int, line.rstrip().split(" ")))
            l[count - 1] = hwl[0]
            u[count - 1] = hwl[1]
            cp[count - 1] = hwl[2:]
        else:
            d = list(map(int, line.rstrip().split(" ")))
        count += 1


    #print(C, P)
    #print(l, u)
    #print(cp, d)
    INF = 999999999

    g = Graph(C+P+2)
    source = 0
    sink = C+P+1

    for i in range(1, C+1):
        g.add_edge(source, i, u[i-1], l[i-1])
        for j in cp[i-1]:
            g.add_edge(i, j+C, 1, 0)

    for i in range(C+1, P+C+1):
        g.add_edge(i, sink, C, d[i-C-1])


    # vyrovnání lb
    gx = Graph(C+P+2+2)
    gx.ub = np.pad((g.ub.copy() - g.lb.copy()), ((0, 2), (0, 2)), 'constant', constant_values=0)
    gx.add_edge(sink, source, INF, 0)


    sx = C+P+2
    tx = C+P+3

    for i in range(1, C+1):
        gx.add_edge(sx, i, l[i-1], 0)

    for i in range(C+1, P+C+1):
        gx.add_edge(i, tx, d[i-C-1], 0)

    gx.add_edge(source, tx, sum(l), 0)
    gx.add_edge(sx, sink, sum(d), 0)

    #print(g.ub)
    #print(gx.ub)


    gx.fordFulkerson(sx,tx)
    #print("----")
    #print(gx.ub)
    #print(gx.flow)

    if np.sum(gx.flow[sx][:]) == np.sum(gx.ub[sx][:]) and np.sum(gx.flow[sx][:])>0:
        #print("ANO, SATURUJE")

        g.flow = gx.flow[:P + C + 2, :P + C + 2].copy() + g.lb.copy()

        g.fordFulkerson(source, sink)
        #print("----")
        # print(g.ub)
        # print(g.lb)

        with open(sys.argv[2], "w") as f:
            for i in range(1, 1 + C):
                for j in range(1, C + P + 1):
                    if g.flow[i][j] == 1:
                        #print(j - C, end=" ")
                        f.write(str(j - C) + " ")
                #print("")
                f.write("\n")
    else:
        #print("NE, NEPŘÍPUSTNÝ TOK!")
        #print(gx.flow[sx][:])
        #print(gx.ub[sx][:])
        with open(sys.argv[2], "w") as f:
            f.write("-1")










