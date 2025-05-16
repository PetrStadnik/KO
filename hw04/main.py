#!/usr/bin/env python3
import sys
import numpy as np


class Graph:
    def __init__(self, size):
        self.size = size
        self.lb = np.zeros((size, size), dtype=int)
        self.ub = np.zeros((size, size), dtype=int)
        self.c = np.zeros((size, size), dtype=float)
        self.flow = np.zeros((size, size), dtype=int)

    def add_edge(self, u, v, upper, lower, cost=0.0):
        self.ub[u][v] = upper
        self.lb[u][v] = lower
        self.c[u][v] = cost

    def residualGraph(self):
        rub = self.ub - self.flow
        rub = rub + np.transpose(self.flow - self.lb)
        rc = self.c.copy()*rub - np.transpose(self.c.copy())
        return rub.astype(int), rc.astype(float)

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

    def find_neg_cycle(self, t, queue, rub, rc):
        s = queue.pop(0)
        path = [s]
        visited = [s]
        value = np.ones(self.size)*np.inf
        pos = 0
        suma = 0
        while True:
            #print(path)
            #print(value)
            if rub[s][t] > 0 > suma + rc[s][t]:
                return path + [(True, int(rub[s][t])), t] if rc[s][t] >= 0 else path + [(False, int(rub[s][t])), t]
            for v in range(2, self.size):
                if v not in visited and value[v] > suma + rc[s][v]:
                    if rub[s][v] > 0 and rc[s][v] >= 0:
                        value[v] = suma + rc[s][v]
                        queue.append((v, pos, path+[(True, int(rub[s][v])), v], suma + rc[s][v], visited + [v]))
                    if rub[s][v] > 0 and rc[s][v] <= 0:
                        value[v] = suma + rc[s][v]
                        queue.append((v, pos, path+[(False, int(rub[s][v])), v], suma + rc[s][v], visited + [v]))
            if queue == []:
                return None
            st = queue.pop(0)
            path = st[2]
            s = st[0]
            suma = st[3]
            visited = st[4]

    def cycle_canceling(self, players, places):
        path = []
        while path is not None:
            rub, rc = self.residualGraph()
            #print(rub)
            start = None
            for i in players:
                path = self.find_neg_cycle(i, [i], rub, rc)
                #print(path)
                if path is not None:
                    start = i
                    break
            if path is None:
                break
            #print(rub)

            tup = path[1::2]
            _, vals = zip(*tup)
            val = min(vals)
            # print(path)
            # print(val)
            # print(self.flow)
            if val == 0:
                break
            while path != [start]:
                u = path.pop(0)
                forward = path.pop(0)[0]
                v = path[0]
                if forward:
                    self.flow[u][v] += 1
                else:
                    self.flow[v][u] -= 1


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


def euklid(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.linalg.norm(a - b))


if __name__ == '__main__':
    n, p, f = None, None, None
    count = 0

    file = open(sys.argv[1], "r")
    for line in file:
        if count == 0:
            n, p = list(map(int, line.rstrip().split(" ")))
            f = [{"x": [], "y": []} for i in range(p)]
        elif count > 0:
            hwl = list(map(int, line.rstrip().split(" ")))
            f[count - 1]["x"] = hwl[0::2]
            f[count - 1]["y"] = hwl[1::2]
        count += 1

    #print(n, p)
    #print(f)
    INF = 999999999
    resstr = ""
    for frames in range(p-1):
    #for frames in range(45, 46):
        graph = Graph(n+n+2)
        source = 0
        sink = 1
        players = range(2, n+2)
        positions = range(n+2, n+2+n)
        for i in players:
            graph.add_edge(source, i, lower=1, upper=1, cost=0)
        for i in positions:
            graph.add_edge(i, sink, lower=1, upper=1, cost=0)
        ii = -1
        for i in players:
            ii += 1
            jj = -1
            for j in positions:
                jj += 1
                graph.add_edge(i, j, lower=0, upper=1, cost=euklid([f[frames]["x"][ii], f[frames]["y"][ii]], [f[frames+1]["x"][jj], f[frames+1]["y"][jj]]))

        #print(graph.c)
        #print(graph.ub)

        gx = Graph(n+n+2+2)
        gx.ub = np.pad((graph.ub.copy() - graph.lb.copy()), ((0, 2), (0, 2)), 'constant', constant_values=0)
        gx.add_edge(sink, source, INF, 0)

        sx = n + n + 2
        tx = n + n + 3

        gx.add_edge(source, tx, n, 0)
        gx.add_edge(sx, sink, n, 0)

        for i in players:
            gx.add_edge(sx, i, 1, 0)

        for i in positions:
            gx.add_edge(i, tx, 1, 0)

        gx.fordFulkerson(sx, tx)
        #print(gx.flow)
        #if gx.flow[sx][sink] == n:
            #print("SATUROVÁNO :-)")
        #else:
            #print("POZOR, NESATUROVÁNO!")

        graph.flow = gx.flow[:n+n+2, :n+n+2].copy() + graph.lb.copy()
        #print(graph.flow)
        #print(graph.c.astype(int))
        #print("residual")
        #print(graph.residualGraph()[0])
        #print(graph.residualGraph()[1].astype(int))
        #print("==============")
        #print(players)

        #print(graph.flow)
        graph.cycle_canceling(players, positions)
        #print(graph.flow)
        #print(graph.residualGraph()[0])
        #print(graph.residualGraph()[1].astype(int))
        #print(graph.flow)
        sol = graph.flow.round()
        for i in players:
            print(np.where(1==sol[i])[0][0]-n-1, end=" ")
            resstr += str(np.where(1==sol[i])[0][0]-n-1) + " "
        print("")
        resstr += "\n"

    with open(sys.argv[2], "w") as f:
        f.write(resstr)



