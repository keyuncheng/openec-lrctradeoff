#!/usr/bin/env python3
import numpy as np
import gurobipy as gp
from gurobipy import GRB

eck = 10
ecl = 2
ecg = 2
ecn = eck + ecl + ecg
ecb = int(eck / ecl)

max_num_racks = eck + ecl

print("(k,l,g): ({}, {}, {})".format(eck, ecl, ecg))
print("(n,b,max_num_racks): ({}, {}, {})".format(ecn, ecb, max_num_racks))

try:
    # Create a new model
    model = gp.Model("lrc-maintenance")

    # Variables

    # a(i,j): number of data blocks in the i-th rack from the j-th local
    # group. lower bound: 0; upper bound: g+1 (each rack stores at most g+1
    # blocks from each local group)
    a = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, lb=0, ub=ecg+1, name="a")

    # b(i,j): number of local parity blocks in rack i for local group j. There
    # is only one local parity block in each local group
    b = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="b")

    # Constraint 1: there are a total of b data blocks in each local group
    for lg_id in range(ecl):
        model.addConstr(a.sum('*', lg_id) == ecb)

    # Constraint 2: there is only one local parity block in each local group
    for lg_id in range(ecl):
        model.addConstr(b.sum('*', lg_id) == 1)

    # x(i): number of blocks in the i-th rack
    x = model.addVars(max_num_racks, vtype=GRB.INTEGER, lb=0, ub=ecg+ecl, name="x")
    for rack_id in range(max_num_racks):
        model.addConstr(x[rack_id] == a.sum(rack_id, '*') + b.sum(rack_id, '*'))

    # I_lg(i,j): Indicator variable that whether the i-th rack stores any
    # block from the j-th local group
    I_lg = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="I_lg")
    for rack_id in range(max_num_racks):
        for lg_id in range(ecl):
            model.addGenConstrIndicator(I_lg[rack_id, lg_id], True, a[rack_id, lg_id] + b[rack_id, lg_id] >= 1)
            model.addGenConstrIndicator(I_lg[rack_id, lg_id], False, a[rack_id, lg_id] + b[rack_id, lg_id] == 0)
    
    # z_j: number of racks the j-th local group spans
    z = model.addVars(ecl, vtype=GRB.INTEGER, lb=0, ub=ecb+1, name="z")
    for lg_id in range(ecl):
        model.addConstr(z[lg_id] == I_lg.sum('*', lg_id))

    # I_b(i): Indicator variable that whether the i-th rack stores any block
    I_b = model.addVars(max_num_racks, vtype=GRB.BINARY, name="I_b")
    for rack_id in range(max_num_racks):
        model.addGenConstrIndicator(I_b[rack_id], True, x[rack_id] >= 1)
        model.addGenConstrIndicator(I_b[rack_id], False, x[rack_id] == 0)

    ################# No need for repair (start)
    # Z: number of racks the entire stripe spans
    Z = model.addVar(vtype=GRB.INTEGER, lb=0, ub=eck+ecl, name="Z")
    model.addConstr(Z == I_b.sum('*'))

    ################# No need for repair (end)

    # Constraint 3: each rack stores at most g+i blocks that spanned by i
    # local groups (single rack fault tolerance)
    for rack_id in range(max_num_racks):
        model.addConstr(x[rack_id] <= ecg + I_lg.sum(rack_id, '*'))
        
    # # Constr 3: each rack stores at most g+1 blocks in each local group
    # for rack_id in range(max_num_racks):
    #     for lg_id in range(ecl):
    #         model.addConstr(a[rack_id, lg_id] + b[rack_id, lg_id] <= g + 1)


    #####################################################################
    # # Optimization goal: minimize R (repair cost)

    # # r_cost(j): repair cost for all data blocks from the j-th local group
    # r = model.addVars(ecl, vtype=GRB.INTEGER, lb=0, ub=eck, name="r")
    # for lg_id in range(ecl):
    #     model.addConstr(r[lg_id] == ecb * (z[lg_id] - 1))
    
    # R = model.addVar(vtype=GRB.INTEGER, lb=0, name="R")
    # R = 1.0 * r.sum('*') / eck

    # # Set objective
    # model.setObjective(R, GRB.MINIMIZE)
    #####################################################################


    #####################################################################
    # Optimization goal: minimize M (maintenance cost)
    # m_cost(i，j) maintenance cost for the data blocks from the j-th local
    # group in the i-th rack

    # m_cost_global_tmp(i,j): tmp variable, representing the maintenance cost
    # to repair the j-th local group in the i-th rack
    m_cost_global_tmp = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, lb=0, ub=eck, name="m_cost_global_tmp")
    for rack_id in range(max_num_racks):
        for lg_id in range(ecl):
            model.addConstr(m_cost_global_tmp[rack_id, lg_id] == (1 - b[rack_id, lg_id]) * (z[lg_id] - 2) + (a[rack_id, lg_id] + b[rack_id, lg_id] - 1) * (Z - 2))

    # m_cost_global(i): maintenance cost for the data blocks in the i-th rack (global repair)
    m_cost_global = model.addVars(max_num_racks, vtype=GRB.INTEGER, lb=0, ub=eck, name="m_cost_global")
    for rack_id in range(max_num_racks):
        model.addConstr(m_cost_global[rack_id] == m_cost_global_tmp.sum(rack_id, '*'))

    # TODO fix bug here
    # I_l(i): Indicator variable that whether the data blocks in j-th local
    # group can be locally repaired in the i-th rack
    I_l = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="I_l")
    for rack_id in range(max_num_racks):
        for lg_id in range(ecl):
            model.addGenConstrIndicator(I_l[rack_id, lg_id], True, a[rack_id, lg_id] + b[rack_id, lg_id] == 1)
            model.addGenConstrIndicator(I_l[rack_id, lg_id], False, a[rack_id, lg_id] + b[rack_id, lg_id] >= 2)
    
    # m_cost(i,j): maintenance cost for each of the data block from the j-th
    # local group in the i-th rack (mixing local and global repair)
    m_cost = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, lb=0, name="m_cost")
    for rack_id in range(max_num_racks):
        for lg_id in range(ecl):
            # model.addConstr(m_cost[rack_id, lg_id] == (I_l[rack_id, lg_id] *
            # (z[lg_id] - 2) + (1 - I_l[rack_id, lg_id]) *
            # m_cost_global[rack_id]))

            model.addConstr(m_cost[rack_id, lg_id] == I_l[rack_id, lg_id] * (z[lg_id] - 2))
            # model.addConstr(m_cost[rack_id, lg_id] == m_cost_global[rack_id])

    # m_cost_sum(i,j): sum of maintenance costs for all the data blocks from the j-th local group in the i-th rack 
    m_cost_sum = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, lb=0, name="m_cost")
    for rack_id in range(max_num_racks):
        for lg_id in range(ecl):
            model.addConstr(m_cost_sum[rack_id, lg_id] == a[rack_id, lg_id] * m_cost[rack_id, lg_id])

    # M: average maintenance cost of the LRC stripe
    M = model.addVar(vtype=GRB.INTEGER, lb=0, name="M")
    model.addConstr(M == m_cost_sum.sum('*', '*') / eck)

    # M = gp.quicksum(a[rack_id, lg_id] * m_cost[rack_id, lg_id] for rack_id in range(max_num_racks) for lg_id in range(ecl)) / eck
    # M = 1.0 * m_cost.sum('*', '*') / eck

    # Set objective
    model.setObjective(M, GRB.MINIMIZE)
    #####################################################################


    # Optimize model
    model.optimize()

    for v in model.getVars():
        print(f"{v.VarName} {v.X:g}")

    print(f"Obj: {model.ObjVal:g}")


except gp.GurobiError as e:
    print(f"Error code {e.errno}: {e}")

except AttributeError:
    print("Encountered an attribute error")
