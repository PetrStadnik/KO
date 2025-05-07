#!/usr/bin/env python3
import sys
import gurobipy as g
import numpy as np

def get_distM(l):
    m = np.zeros((n+2,n+2), dtype=np.uint64)
    for i in range(n):
        for j in range(n):
            if i != j:
                m[j, i] = np.sum(np.abs(l[i, :, 0, :] - l[j, :, -1, :]))

    return m







if __name__ == '__main__':
    count = 0

    l, n, w, h = None, None, None, None
    file = open(sys.argv[1], "r")
    for line in file:
        if count == 0:
            n, w, h = list(map(int, line.rstrip().split(" ")))
            l = np.empty((n, h, w, 3), dtype=int)
            #print(n,w,h,l)
        else:
            l[count-1] = np.array(list(map(int, line.rstrip().split(" ")))).reshape(h, w, 3)
        count += 1



    #print(l)
    #print(l[0, :, 0, :])
    #print(l[0, :, -1, :])


    d = get_distM(l)
    #print(d)

    m = g.Model()
    m.setParam("OutputFlag", 0)
    m.Params.lazyConstraints = 1

    x = m.addVars(n+2, n+2, vtype=g.GRB.BINARY)

    m.addConstr(1 == x[n + 1, n])
    m.addConstrs(1 == x.sum(i, "*") for i in range(n + 2))
    m.addConstrs(1 == x.sum("*", i) for i in range(n + 2))
    m.addConstrs(0 == x[i, i] for i in range(n + 2))


    m.setObjective(g.quicksum(x[i, j] * d[i, j] for i in range(n+2) for j in range(n+2)), sense=g.GRB.MINIMIZE)


    def my_callback(model, where):
        if where == g.GRB.Callback.MIPSOL:

            e = model.cbGetSolution(x)
            t = np.array(list(e.values())).reshape(n+2, n+2).round().astype(int)
            #print(t)
            #print(t)
            #print(n)
            index = 0
            start = index
            sv = []
            while (start != index) or len(sv) == 0:
                #print(np.where(t[ver, :] == 1))
                index = np.where(t[index, :] == 1)[0][0]
                sv.append(index)
                #print(i)

            if len(sv) < n + 2:
                model.cbLazy(g.quicksum(x[i, j] for i in sv for j in sv) <= len(sv)-1)


    m.optimize(my_callback)

    #print(int(m.objVal))

    v = n
    with open(sys.argv[2], "w") as f:
        while v != n+1:
            if v != n:
                print(" ", end="")
                f.write(" ")
            for i in range(n+2):
                if x[v, i].X == 1:
                    if i != n+1:
                        print(i+1, end="")
                        f.write(str(int(i+1)))
                    v = i
                    break

