#!/usr/bin/env python3
import sys
import gurobipy as gur
import numpy as np

if __name__ == '__main__':

    M, L, F, U, g, s, d, h, p, friends = [None]*10

    count = -1

    file = open(sys.argv[1], "r")
    for line in file:
        count +=1
        if count == 0:
            M, L, F, U = list(map(int, line.rstrip().split(" ")))
            friends = [0] * F
        elif count == 1:
            g = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 2:
            s = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 3:
            d = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 4:
            h = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 5:
            p = np.array(list(map(int, line.rstrip().split(" "))))
        else:
            friends[count-6] = tuple(map(int, line.rstrip().split(" ")))


    print(M, L, F, U)
    print(friends)


    g0 = np.where(g == 0)[0]
    g1 = np.where(g == 1)[0]
    g2 = np.where(g == 2)[0]

    print(g0, g1, g2)

    m = gur.Model()

    asg = m.addVars(M, L, vtype=gur.GRB.BINARY)
    for i in range(M):
        m.addConstr(asg.sum(i, "*") <= 1)

    for i in range(L):
        m.addConstr(asg.sum("*", i) <= 1)

    m.addConstr(gur.quicksum(asg.sum(i,"*") for i in g1) + gur.quicksum(asg.sum(i,"*") for i in g2) >= gur.quicksum(asg.sum(i,"*") for i in g0))
    m.addConstr(gur.quicksum(asg.sum(i, "*") for i in g1) + gur.quicksum(asg.sum(i, "*") for i in g0) >= gur.quicksum(asg.sum(i, "*") for i in g2))
    m.addConstr(gur.quicksum(asg.sum(i, "*") for i in g2) + gur.quicksum(asg.sum(i, "*") for i in g0) >= gur.quicksum(asg.sum(i, "*") for i in g1))

    for i in range(L):
        m.addConstr(gur.quicksum(asg[j,i]*s[j] for j in range(M)) <= d[i])

    pairs = m.addVars(F, vtype=gur.GRB.BINARY)
    for i in range(len(friends)):
        m.addConstr(gur.quicksum(asg[friends[i][0], l] for l in range(L))*0.6 + gur.quicksum(asg[friends[i][1], l] for l in range(L))*0.6 >= pairs[i])

    production = m.addVar(lb=0, vtype=gur.GRB.INTEGER)
    happiness = m.addVar(lb=0, vtype=gur.GRB.INTEGER)
    happypair = m.addVar(lb=0, vtype=gur.GRB.INTEGER)

    m.addConstr(production == gur.quicksum(asg[j,i]*p[j] for i in range(L) for j in range(M)))
    m.addConstr(happiness == gur.quicksum(asg[j,i]*h[j] for i in range(L) for j in range(M)))
    m.addConstr(happypair == pairs.sum("*")*5)

    OR = m.addVar(vtype=gur.GRB.BINARY)
    m.addConstr(production >= U*OR)
    m.addConstr(happiness + happypair >= U*(1-OR))




    m.setObjective(production + happiness + happypair, sense=gur.GRB.MAXIMIZE)
    m.optimize()

    if m.status == gur.GRB.OPTIMAL:
        print("OPTIMAL FOUND!")
        print(round(m.ObjVal))
        print(production.X, happiness.X, happypair.X)

        with open(sys.argv[2], "w") as f:
            f.write(str(round(m.ObjVal))+"\n")
            for i in range(M):
                pos = -1
                for j in range(L):
                    if round(asg[i, j].X) == 1:
                        pos = j
                print(round(pos))
                f.write(str(round(pos))+" ")
    else:
        print("INFEASIBLE!!!")
        with open(sys.argv[2], "w") as f:
            f.write(str(round(-1)))


