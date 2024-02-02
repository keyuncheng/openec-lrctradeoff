#!/usr/bin/env python3
import numpy as np
import gurobipy as gp
from gurobipy import GRB

eck = 10
ecl = 2
ecg = 2
ecn = eck + ecl + ecg
ecb = eck / ecl

max_num_racks = ecn

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

    # auxiliary variables: x, I_lg, z, Z

    # x(i): number of blocks in the i-th rack
    x = model.addVars(max_num_racks, vtype=GRB.INTEGER, lb=0, ub=ecg+ecl, name="x")
    for rack_id in range(max_num_racks):
        x[rack_id] = a.sum(rack_id, '*') + b.sum(rack_id, '*')

    # I_lg(i,j): Indicator variable that whether the j-th local group spans
    # the i-th rack
    I_lg = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="I_lg")
    for rack_id in range(max_num_racks):
        for lg_id in range(ecl):
            model.addGenConstrIndicator(I_lg[rack_id, lg_id], True, a[rack_id, lg_id] + b[rack_id, lg_id] >= 1)
    
    # z_j: number of racks the j-th local group spans
    z = model.addVars(ecl, vtype=GRB.INTEGER, lb=0, ub=ecb, name="z")
    for lg_id in range(ecl):
        z[lg_id] = I_lg.sum('*', lg_id)

    # I_b(i): Indicator variable that whether any block is stored in the i-th rack
    I_b = model.addVars(max_num_racks, vtype=GRB.BINARY, name="I_b")
    for rack_id in range(max_num_racks):
        model.addGenConstrIndicator(I_b[rack_id], True, x[rack_id] >= 1)

    # Z: number of racks the entire stripe spans
    Z = I_b.sum('*')

    # Constraint 3: each rack stores at most g+i blocks that spanned by i
    # local groups (single rack fault tolerance)
    for rack_id in range(max_num_racks):
        model.addConstr(x[rack_id] <= ecg + I_lg.sum(rack_id, '*'))
        
    # # Constr 3: each rack stores at most g+1 blocks in each local group
    # for rack_id in range(max_num_racks):
    #     for lg_id in range(ecl):
    #         model.addConstr(a[rack_id, lg_id] + b[rack_id, lg_id] <= g + 1)

    # Optimization goal: minimize M (maintenance cost)
    # m_cost(i) maintenance cost for the i-th rack
        
    # TODO
    m_cost = model.addVars(max_num_racks, vtype=GRB.INTEGER, lb=0, name="m_cost")
    for lg_id in range(ecl):
        m_cost[rack_id] += (1 - b[i][j]) * (z[i] - 2) + (a[i][j] - 1 + b[i][j]) * (Z - 2)

    


except gp.GurobiError as e:
    print(f"Error code {e.errno}: {e}")

except AttributeError:
    print("Encountered an attribute error")
