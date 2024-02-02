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

    # Create variables

    # a(i,j) number of data blocks in rack i for local group j, lower bound:
    # 0; upper bound: g+1 (each rack stores at most g+1 blocks from each local
    # group)
    a = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, lb=0, ub=ecg+1, name="a")
    b = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="b") # a(i,j) number of data blocks in rack i for local group j

    # Constraint 1: there are a total of b data blocks in each local group
    for lg_id in range(ecl):
        model.addConstr(a.sum('*', lg_id) == ecb)

    # Constraint 2: there is only one local parity block in each local group
    for lg_id in range(ecl):
        model.addConstr(b.sum('*', lg_id) == 1)

    # auxiliary variables: x, I_span

    # number of blocks in a rack
    x = model.addVars(max_num_racks, vtype=GRB.INTEGER, lb=0, ub=ecg+ecl, name="x")
    for rack_id in range(max_num_racks):
        x[rack_id] = a.sum(rack_id, '*') + b.sum(rack_id, '*')

    # Indicator variable that whether local group j is spanned in rack i
    I_span = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="I_span")
    for rack_id in range(max_num_racks):
        for lg_id in range(ecl):
            model.addGenConstrIndicator(I_span[rack_id, lg_id], True, a[rack_id, lg_id] + b[rack_id, lg_id] >= 1)
    
    # Constraint 3: each rack stores at most g+i blocks that spanned by i
    # local groups (single rack fault tolerance)
    for rack_id in range(max_num_racks):
        model.addConstr(x[rack_id] <= ecg + I_span.sum(rack_id, '*'))
        
    # # Constr 3: each rack stores at most g+1 blocks in each local group
    # for rack_id in range(max_num_racks):
    #     for lg_id in range(ecl):
    #         model.addConstr(a[rack_id, lg_id] + b[rack_id, lg_id] <= g + 1)

    # Optimization goal: minimize M (maintenance cost)



except gp.GurobiError as e:
    print(f"Error code {e.errno}: {e}")

except AttributeError:
    print("Encountered an attribute error")
