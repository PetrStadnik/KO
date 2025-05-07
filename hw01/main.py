#!/usr/bin/env python3
import sys
import gurobipy as g

if __name__ == '__main__':
    count = 0
    l = [0, 0, 0]
    file = open(sys.argv[1], "r")
    for line in file:
        l[count] = line.rstrip()
        count += 1
        if count >= 3:
            break
    print(l)

    d = list(map(int, l[0].split(" ")))
    e = list(map(int, l[1].split(" ")))
    D = int(l[2])

    wd = d + d + d + d + d + e + e

    m = g.Model()
    m.setParam("OutputFlag", 0)

    xs = m.addVars(len(wd), lb=0, vtype=g.GRB.INTEGER, name=[f"x{i}" for i in range(len(wd))])
    z = m.addVars(len(wd), vtype=g.GRB.INTEGER, lb=0)

    for i in range(len(wd)):
        m.addConstr(wd[i] - g.quicksum(xs[j % len(wd)] for j in range(i - 7, i + 1)) <= D)

    m.addConstrs(g.quicksum(xs[j % len(wd)] for j in range(i - 7, i + 1)) - wd[i] <= z[i] for i in range(len(wd)))
    m.addConstrs(wd[i] - g.quicksum(xs[j % len(wd)] for j in range(i - 7, i + 1)) <= z[i] for i in range(len(wd)))

    m.setObjective(z.sum(), sense=g.GRB.MINIMIZE)


    m.optimize()
    print(int(m.objVal))
    for i in range(len(wd)):
        print(int(xs[i].X), end=" ")

    with open(sys.argv[2], "w") as f:
        f.write(str(int(m.objVal))+"\n")
        for i in range(len(wd)-1):
            f.write(str(int(xs[i].X)) + " ")
        f.write(str(int(xs[len(wd)-1].X)))
        #f.write("2 0 4 16 0 1 1 0 0 0 7 12 0 0 6 4 2 0 0 6 0 0 0 0 0 0 0 16 0 1 5 0 0 0 3 12 0 0 6 4 2 0 0 6 0 0 0 0 0 0 0 16 0 1 8 0 0 0 0 12 0 0 6 4 2 0 0 6 0 0 0 0 0 0 0 10 0 1 8 1 5 0 0 6 0 0 6 4 5 3 0 0 0 0 0 0 6 0 0 11 0 0 0 0 11 0 3 7 0 0 6 4 5 0 2 1 0 0 0 0 0 0 2 5 0 0 4 0 0 0 3 3 0 0 3 2 1 0 3 0 0 0 0 0 0 0 3 5 0 0 3 0 0 0 4 3 0 0 2 3 0 0 4 0 0 0 0 0")

