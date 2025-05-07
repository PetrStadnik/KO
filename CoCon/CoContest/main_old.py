#!/usr/bin/env python3
import sys
import gurobipy as g
import numpy as np

if __name__ == '__main__':

    BP, M, N, n, H = None, None, None, None, None
    count = 0
    file = open(sys.argv[1], "r")
    for line in file:
        if count == 0:
            M, N = list(map(int, line.rstrip().split(" ")))
        elif count == 1:
            n = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 2:
            H = np.array(list(map(int, line.rstrip().split(" "))))
            BP = np.empty(N, dtype=int)
            p = dict()
            h = dict()
        else:
            l = list(map(int, line.rstrip().split(" ")))
            BP[count-3] = int(round(l[0]))
            p[count-3] = l[1::2]
            h[count-3] = l[2::2]
        count += 1

    print(M, N)
    print(h) #výšky zásilek
    print(p)
    print(H) #výšky boxu
    print(BP)
    print(n)


m = g.Model()

#m.setParam('OutputFlag', 0)

BM = 999999999
pol = [0]*N
ass = [0]*N

all = m.addVars(N, vtype=g.GRB.BINARY)
for i in range(N):
    pol[i] = m.addVars(len(h[i]), lb=0, ub=M, vtype=g.GRB.INTEGER)
    ass[i] = m.addVars(len(h[i]), vtype=g.GRB.BINARY)

for i in range(N):
    for j in range(len(h[i])):
        m.addConstr(ass[i][j]*BM >= pol[i][j])
        m.addConstr(ass[i][j] <= BM*pol[i][j])


for i in range(N):
    for j in range(N):
        if i != j:
            for ii in range(len(h[i])):
                for jj in range(len(h[j])):
                        z = m.addVar(vtype=g.GRB.BINARY)
                        m.addConstr(pol[i][ii] - pol[j][jj] <= ass[i][ii]*(-0.9) + BM * z)
                        m.addConstr(pol[i][ii] - pol[j][jj] >= ass[j][jj]*0.9 - BM * (1-z))

for i in range(N):
    m.addConstr(ass[i].sum() - len(h[i]) + 0.9 <= all[i])
    m.addConstr(ass[i].sum() >= all[i] * len(h[i]))

m.addVars(M, lb=0, vtype=g.GRB.INTEGER)
g.quicksum()

m.setObjective(g.quicksum(p[i][j]*ass[i][j] for i in range(N) for j in range(len(h[i]))) + g.quicksum(all[i]*BP[i] for i in range(N)), sense=g.GRB.MAXIMIZE)

m.optimize()
if m.status == g.GRB.OPTIMAL:
    print("OPTIMAL FOUND!")

print(round(m.ObjVal))


with open(sys.argv[2], "w") as f:
    f.write(str(round(m.ObjVal))+"\n")
    for i in range(N):
        for j in range(len(h[i])):
            print(round(pol[i][j].X))
            f.write(str(round(pol[i][j].X)) + "\n")

