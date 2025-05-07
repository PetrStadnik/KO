#!/usr/bin/env python3
import sys
import gurobipy as g
import numpy as np

if __name__ == '__main__':

    BP, M, N, n, H, W, cust = None, None, None, None, None, None, None
    count = 0

    ll = 0
    file = open(sys.argv[1], "r")
    for line in file:
        if count == 0:
            M, N = list(map(int, line.rstrip().split(" ")))
        elif count == 1:
            n = np.array(list(map(int, line.rstrip().split(" "))))
        elif count == 2:
            hwl = list(map(int, line.rstrip().split(" ")))
            W = np.array(hwl[0::2])
            H = np.array(hwl[1::2])
            BP = np.empty(N, dtype=int)
            p = []
            w = []
            h = []
            cust = [0] * N
        else:
            l = list(map(int, line.rstrip().split(" ")))
            BP[count-3] = int(round(l[0]))
            cust[count-3] = list(range(ll, ll + len(l[1::3])))
            p = p + l[1::3]
            w = w + l[2::3]
            h = h + l[3::3]
            ll = ll + len(l[1::3])
        count += 1

    #print(M, N)
    #print(w)
    #print(h) #výšky zásilek
    #print(p)
    #print(H) #výšky boxu
    #print(BP)
    #print(n)
    #print(cust)
    #print(ll)
    """
    zasilky = list(range(ll))
    for i in range(ll):
        zasilky[i] = {"p": p[i], "w": w[i], "h": h[i]}

    zasilky.sort(key=lambda x: x["p"])
    """
    m = g.Model()

    m.setParam('OutputFlag', 0)
    m.setParam("TimeLimit", float(sys.argv[3])-6)

    BM = 9999999



    box = m.addVars(ll, M, vtype=g.GRB.BINARY)

    for i in range(ll):
        m.addConstr(box.sum(i, "*") <= 1)

    r = m.addVars(ll, vtype=g.GRB.BINARY)
    x = m.addVars(ll, vtype=g.GRB.INTEGER, lb=0)
    y = m.addVars(ll, vtype=g.GRB.INTEGER, lb=0)
    for i in range(M):
        m.addConstr(g.quicksum(box[j, i]*h[j]*w[j] for j in range(ll)) <= H[i]*W[i])
        m.addConstrs(box[j, i] * w[j] * (1-r[j]) <= W[i] - x[j] for j in range(ll))
        m.addConstrs(box[j, i] * h[j] * (1-r[j]) <= H[i] - y[j] for j in range(ll))
        m.addConstrs(box[j, i] * w[j] * r[j] <= H[i] - y[j] for j in range(ll))
        m.addConstrs(box[j, i] * h[j] * r[j] <= W[i] - x[j] for j in range(ll) )

    all = m.addVars(N, vtype=g.GRB.BINARY)
    for i in range(N):
        m.addConstr(g.quicksum(box[j,k] for j in cust[i] for k in range(M)) >= all[i] * len(cust[i]))

    ctb = m.addVars(N, M, vtype=g.GRB.BINARY)
    for i in range(M):
        m.addConstr(ctb.sum("*", i) <= 1)

    for i in range(N):
        for j in range(M):
            m.addConstr(ctb[i, j]*BM >= g.quicksum(box[q, j] for q in cust[i]))


    same = m.addVars(ll, ll, vtype=g.GRB.BINARY)
    for i in range(ll-1):
        for j in range(i+1, ll):
            for k in range(M):
                m.addConstr(same[i,j] +1 >= 0.7*box[i, k] + 0.7*box[j, k])
                #m.addConstr(same[i,j] <= 0.7 * box[i, k] + 0.7 * box[j, k])

            o = m.addVar(vtype=g.GRB.BINARY)
            m.addConstr(x[i] + w[i] <= x[j] + (1 - same[i,j]) * BM + r[i] * BM + o*BM)
            m.addConstr(-(1-o)*BM + y[i] + h[i] <= y[j] + (1 - same[i,j]) * BM + r[i] * BM)
            m.addConstr(-o*BM + x[i] + h[i] <= x[j] + (1 - same[i,j]) * BM + (1-r[i]) * BM)
            m.addConstr(-(1-o)*BM + y[i] + w[i] <= y[j] + (1 - same[i,j]) * BM + (1-r[i]) * BM)



    m.setObjective(g.quicksum(p[i]*box[i, j] for i in range(ll) for j in range(M)) + g.quicksum(all[i]*BP[i] for i in range(N)), sense=g.GRB.MAXIMIZE)

    def my_callback(model, where):
        if where == g.GRB.Callback.MIPSOL:

            e = model.cbGetSolution(box)
            rr = model.cbGetSolution(r)
            rot =  np.array(list(e.values())).reshape(ll).round().astype(int)
            t = np.array(list(e.values())).reshape(ll, M).round().astype(int)
            b = list(range(M))
            for i in range(M):
                b[i] = np.where(t[:, i]==1)[0].tolist()

            for i in range(M):
                for j in b[i]:
                    pass


            #print("\n=== e:"+str(e))
            #print("\n=== b:"+str(b))
            #model.cbLazy(g.quicksum(x[i, j] for i in sv for j in sv) <= len(sv)-1)

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
            #print(str(round(pos))+" " +str(round(x[i].X)) + " " + str(round(y[i].X)) + " "+str(round(r[i].X)))
            f.write(str(round(pos))+" " +str(round(x[i].X)) + " " + str(round(y[i].X)) + " "+str(round(r[i].X))+"\n")

