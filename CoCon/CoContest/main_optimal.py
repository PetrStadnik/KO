#!/usr/bin/env python3
import sys
import gurobipy as g
import numpy as np

if __name__ == '__main__':

    BP, M, N, n, H, cust = None, None, None, None, None, None
    count = 0

    ll = 0
    file = open(sys.argv[1], "r")
    for line in file:
        if count == 0:
            M, N = list(map(int, line.rstrip().split(" ")))
        elif count == 1:
            n = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 2:
            H = np.array(list(map(int, line.rstrip().split(" "))))
            BP = np.empty(N, dtype=int)
            p = []
            h = []
            cust = [0] * N
        else:
            l = list(map(int, line.rstrip().split(" ")))
            BP[count-3] = int(round(l[0]))
            cust[count-3] = list(range(ll, ll + len(l[1::2])))
            p = p + l[1::2]
            h = h + l[2::2]
            ll = ll + len(l[1::2])
        count += 1

    print(M, N)
    print(h) #výšky zásilek
    print(p)
    print(H) #výšky boxu
    print(BP)
    print(n)
    print(cust)
    print(ll)


m = g.Model()

#m.setParam('OutputFlag', 0)

BM = 999999999



box = m.addVars(ll, M, vtype=g.GRB.BINARY)

for i in range(ll):
    m.addConstr(box.sum(i, "*") <= 1)

for i in range(M):
    m.addConstr(g.quicksum(box[j, i]*h[j] for j in range(ll)) <= H[i])


all = m.addVars(N, vtype=g.GRB.BINARY)
for i in range(N):
    m.addConstr(g.quicksum(box[j,k] for j in cust[i] for k in range(M)) - len(cust[i]) + 0.9 <= all[i])
    m.addConstr(g.quicksum(box[j,k] for j in cust[i] for k in range(M)) >= all[i] * len(cust[i]))

ctb = m.addVars(N, M, vtype=g.GRB.BINARY)
for i in range(M):
    m.addConstr(ctb.sum("*", i) <= 1)

for i in range(N):
    for j in range(M):
        m.addConstr(ctb[i, j]*BM >= g.quicksum(box[q, j] for q in cust[i]))



m.setObjective(g.quicksum(p[i]*box[i, j] for i in range(ll) for j in range(M)) + g.quicksum(all[i]*BP[i] for i in range(N)), sense=g.GRB.MAXIMIZE)

m.optimize()
if m.status == g.GRB.OPTIMAL:
    print("OPTIMAL FOUND!")

print(round(m.ObjVal))


with open(sys.argv[2], "w") as f:
    f.write(str(round(m.ObjVal))+"\n")
    for i in range(ll):
        pos = 0
        for j in range(M):
            if round(box[i, j].X) == 1:
                pos = j + 1
        print(round(pos))
        f.write(str(round(pos))+"\n")


