#!/usr/bin/env python3
import sys
import gurobipy as gur
import numpy as np

if __name__ == '__main__':

    M, P, C, U, t, n, s, d, comp, l, g = [None]*11

    count = -1

    file = open(sys.argv[1], "r")
    for line in file:
        count += 1
        if count == 0:
            M, P, C, U = list(map(int, line.rstrip().split(" ")))
            comp = [0] * C
        elif count == 1:
            t = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 2:
            n = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 3:
            s = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 4:
            d = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 5:
            l = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 6:
            g = np.array(list(map(int, line.rstrip().split(" "))))
        else:
            if count > 6 + C:
                break
            else:
                comp[count-7] = tuple(map(int, line.rstrip().split(" ")))


    print(M, P, C, U)
    print(comp)


    t0 = np.where(t == 0)[0]
    t1 = np.where(t == 1)[0]
    t2 = np.where(t == 2)[0]


    m = gur.Model()

    asg = m.addVars(M, P, vtype=gur.GRB.BINARY)
    for i in range(M):
        m.addConstr(asg.sum(i, "*") <= 1)

    for i in range(P):
        m.addConstr(asg.sum("*", i) <= 1)

    m.addConstr(gur.quicksum(asg.sum(i,"*") for i in t1) >= n[1])
    m.addConstr(gur.quicksum(asg.sum(i, "*") for i in t2) >= n[2])
    m.addConstr(gur.quicksum(asg.sum(i, "*") for i in t0) >= n[0])

    for i in range(P):
        m.addConstr(gur.quicksum(asg[j,i]*s[j] for j in range(M)) <= d[i])

    pairs = m.addVars(C, vtype=gur.GRB.BINARY)
    for i in range(len(comp)):
        m.addConstr(gur.quicksum(asg[comp[i][0], l] for l in range(P))*0.6 + gur.quicksum(asg[comp[i][1], l] for l in range(P))*0.6 >= pairs[i])



    ladies_popularity = m.addVar(lb=0, vtype=gur.GRB.INTEGER)
    guys_popularity = m.addVar(lb=0, vtype=gur.GRB.INTEGER)
    comppair = m.addVar(lb=0, vtype=gur.GRB.INTEGER)

    m.addConstr(ladies_popularity == gur.quicksum(asg[j,i]*l[j] for i in range(P) for j in range(M)))
    m.addConstr(guys_popularity == gur.quicksum(asg[j,i]*g[j] for i in range(P) for j in range(M)))
    m.addConstr(comppair == pairs.sum("*")*10)


    OR = m.addVar(vtype=gur.GRB.BINARY)
    m.addConstr(ladies_popularity >= U*OR)
    m.addConstr(guys_popularity >= U*(1-OR))

    m.setObjective(ladies_popularity+guys_popularity+comppair, gur.GRB.MAXIMIZE)

    m.optimize()

    if m.status == gur.GRB.OPTIMAL:
        print("OPTIMAL FOUND!")
        print(round(m.ObjVal))

        with open(sys.argv[2], "w") as f:
            f.write(str(round(m.ObjVal))+"\n")
            for i in range(M):
                pos = -1
                for j in range(P):
                    if round(asg[i, j].X) == 1:
                        pos = j
                print(round(pos))
                f.write(str(round(pos))+" ")
    else:
        print("INFEASIBLE!!!")
        with open(sys.argv[2], "w") as f:
            f.write(str(round(-1)))