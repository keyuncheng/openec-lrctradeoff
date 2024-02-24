#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
from pathlib import Path
import numpy as np
import gurobipy as gp
from gurobipy import GRB


def parse_args(cmd_args):
    arg_parser = argparse.ArgumentParser(description="optimal maintenance cost and repair cost for LRC") 

    # Input parameters: (k,l,g)
    arg_parser.add_argument("-eck", type=int, required=True, help="eck")
    arg_parser.add_argument("-ecl", type=int, required=True, help="ecl")
    arg_parser.add_argument("-ecg", type=int, required=True, help="ecg")
    arg_parser.add_argument("-problem", type=str, required=True, help="optimization problem [r/m] (r: optimal repair cost; m: optimal maintenance cost)")
    
    
    args = arg_parser.parse_args(cmd_args)
    return args

def exec_cmd(cmd, exec=False):
    print("Execute Command: {}".format(cmd))
    msg = ""
    if exec == True:
        return_str, stderr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
        msg = return_str.decode().strip()
        print(msg)
    return msg

def check_params(eck, ecl, ecg):
    if eck % ecl != 0:
        print("Error: k is not a multiple of l")
        return False
    return True

def main():
    args = parse_args(sys.argv[1:])
    if not args:
        exit()

    # Input parameters: (k,l,g)
    eck = args.eck 
    ecl = args.ecl 
    ecg = args.ecg 

    # check parameters
    if check_params(eck, ecl, ecg) == False:
        return

    ecb = int(eck / ecl)
    ecn = eck + ecl + ecg
    max_num_racks = ecn

    print("Input parameters: Azure-LRC(k,l,g) = ({},{},{})".format(eck, ecl, ecg))
    print("Derived parameters: (n,b,max_num_racks): ({}, {}, {})".format(ecn, ecb, max_num_racks))

    try:
        # Create a new model
        model = gp.Model("lrc-optimization")

        ########################## Input Variables ##########################

        # alpha(i,j): number of data blocks stored in rack R_i from the local
        # group G_j. Type: non-negative integer
        alpha = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, lb=0, name="alpha")

        # beta(i,j): number of local parity blocks stored in rack R_i from the
        # local group G_j.  Type: binary
        beta = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="beta")

        # gamma(i): number of global parity blocks stored in rack R_i. Type:
        # non-negative integer
        gamma = model.addVars(max_num_racks, vtype=GRB.INTEGER, lb=0, name="gamma")

        #####################################################################

        ####################### Constraints #################################

        # Constraint 1: each local group has b data blocks
        for lg_id in range(ecl):
            model.addConstr(alpha.sum('*', lg_id) == ecb)

        # Constraint 2: each local group has one local parity block
        for lg_id in range(ecl):
            model.addConstr(beta.sum('*', lg_id) == 1)

        # Constraint 3: each stripe has g global parity blocks
        model.addConstr(gamma.sum('*') == ecg)

        # Constraint 4: each rack stores at most g+i blocks spanned by i
        # local groups, subject to single-rack fault tolerance
        
        # I_blk_lg(i,j): Indicator variable; check whether rack R_i stores any
        # block from local group G_j.
        I_blk_lg = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="I_blk_lg")
        for rack_id in range(max_num_racks):
            for lg_id in range(ecl):
                model.addGenConstrIndicator(I_blk_lg[rack_id, lg_id], True, alpha[rack_id, lg_id] + beta[rack_id, lg_id] >= 1)
                model.addGenConstrIndicator(I_blk_lg[rack_id, lg_id], False, alpha[rack_id, lg_id] + beta[rack_id, lg_id] == 0)

        for rack_id in range(max_num_racks):
            model.addConstr(alpha.sum(rack_id, '*') + beta.sum(rack_id, '*') + gamma[rack_id] <= ecg + I_blk_lg.sum(rack_id, '*'))
        
        #####################################################################

        if args.problem == "r":
            ########### Optimization goal: minimize repair cost #############

            # I_R(i): Indicator variable; check whether rack R_i stores any block
            I_R = model.addVars(max_num_racks, vtype=GRB.BINARY, name="I_R")
            for rack_id in range(max_num_racks):
                model.addGenConstrIndicator(I_R[rack_id], True, alpha.sum(rack_id, '*') + beta.sum(rack_id, '*') + gamma[rack_id] >= 1)
                model.addGenConstrIndicator(I_R[rack_id], False, alpha.sum(rack_id, '*') + beta.sum(rack_id, '*') + gamma[rack_id] == 0)

            # z: number of racks spanned by the stripe
            z = model.addVar(vtype=GRB.INTEGER, name="z")
            model.addConstr(z == I_R.sum('*'))

            # # I_alpha(): Indicator variable; check whether rack R_i stores any
            # # data block from local group G_j (I_alpha(i,j) = 1 when
            # # alpha(i,j) >= 1)
            # I_alpha = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="I_alpha")
            # for rack_id in range(max_num_racks):
            #     for lg_id in range(ecl):
            #         model.addGenConstrIndicator(I_alpha[rack_id, lg_id], True, alpha[rack_id, lg_id] >= 1)
            #         model.addGenConstrIndicator(I_alpha[rack_id, lg_id], False, alpha[rack_id, lg_id] == 0)

            # delta(j): number of racks spanned by local group G_j
            delta = model.addVars(ecl, vtype=GRB.INTEGER, name="delta")
            for lg_id in range(ecl):
                model.addConstr(delta[lg_id] == I_blk_lg.sum('*', lg_id))

            # r_cost(i,j): repair cost of data blocks of rack R_i from the local
            # group G_j

            # version 1 (the blocks in each local group have the same r_cost)
            r_cost_lg = model.addVars(ecl, vtype=GRB.INTEGER, name="r_cost_lg")
            for lg_id in range(ecl):
                model.addConstr(r_cost_lg[lg_id] == ecb * (delta[lg_id] - 1))
            
            # ARC: average repair cost of the LRC stripe (of all data blocks)
            ARC = model.addVar(vtype=GRB.CONTINUOUS, name="ARC")
            model.addConstr(ARC == r_cost_lg.sum('*') / eck)

            # # version 2
            # r_cost = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, name="r_cost")
            # for rack_id in range(max_num_racks):
            #     for lg_id in range(ecl):
            #         model.addConstr((I_alpha[rack_id, lg_id] == 0) >> (r_cost[rack_id, lg_id] == 0))
            #         model.addConstr((I_alpha[rack_id, lg_id] == 1) >> (r_cost[rack_id, lg_id] == delta[lg_id] - 1))

            # # weighted r_cost(i,j): r_cost_weighted(i,j) = alpha(i,j) * r_cost(i,j)
            # r_cost_weighted = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, name="r_cost_weighted")
            # for rack_id in range(max_num_racks):
            #     for lg_id in range(ecl):
            #         model.addConstr(r_cost_weighted[rack_id, lg_id] == alpha[rack_id, lg_id] * r_cost[rack_id, lg_id])
            
            # # ARC: average repair cost of the LRC stripe (of all data blocks)
            # ARC = model.addVar(vtype=GRB.CONTINUOUS, name="ARC")
            # model.addConstr(ARC == r_cost_weighted.sum('*', '*') / eck)

            # Set objective
            model.setObjective(ARC, GRB.MINIMIZE)

            # Start from an initial solution (combined locality)
            for rack_id in range(max_num_racks):
                for lg_id in range(ecl):
                    alpha[rack_id, lg_id].Start = 0
                    beta[ecb, lg_id].Start = 0
                gamma[rack_id].Start = 0

            max_blocks_per_rack = ecg + 1 # g+1 blocks per rack
            cur_rack_id = 0
            for lg_id in range(ecl):
                remaining_dblocks = ecb
                while remaining_dblocks > 0:
                    num_blocks = max_blocks_per_rack if remaining_dblocks - max_blocks_per_rack > 0 else remaining_dblocks
                    alpha[cur_rack_id, lg_id].Start = num_blocks
                    remaining_dblocks -= num_blocks
                    cur_rack_id += 1
                # if the last rack stores g+1 data blocks, need another rack to
                # store the local parity block
                if ecb % max_blocks_per_rack != 0:
                    beta[cur_rack_id - 1, lg_id].Start = 1
                else:
                    beta[cur_rack_id, lg_id].Start = 1
                    cur_rack_id += 1
            gamma[cur_rack_id].Start = ecg
            #####################################################################
        elif args.problem == "m":
            ######### Optimization goal: minimize maintenance cost ###########
            # m_cost(i，j) maintenance cost for the data blocks from the j-th
            # local group in the i-th rack

            # I_R(i): Indicator variable; check whether rack R_i stores any block
            I_R = model.addVars(max_num_racks, vtype=GRB.BINARY, name="I_R")
            for rack_id in range(max_num_racks):
                model.addGenConstrIndicator(I_R[rack_id], True, alpha.sum(rack_id, '*') + beta.sum(rack_id, '*') + gamma[rack_id] >= 1)
                model.addGenConstrIndicator(I_R[rack_id], False, alpha.sum(rack_id, '*') + beta.sum(rack_id, '*') + gamma[rack_id] == 0)

            # z: number of racks spanned by the stripe
            z = model.addVar(vtype=GRB.INTEGER, name="z")
            model.addConstr(z == I_R.sum('*'))

            # I_alpha(): Indicator variable; check whether rack R_i stores any
            # data block from local group G_j (I_alpha(i,j) = 1 when
            # alpha(i,j) >= 1)
            I_alpha = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="I_alpha")
            for rack_id in range(max_num_racks):
                for lg_id in range(ecl):
                    model.addGenConstrIndicator(I_alpha[rack_id, lg_id], True, alpha[rack_id, lg_id] >= 1)
                    model.addGenConstrIndicator(I_alpha[rack_id, lg_id], False, alpha[rack_id, lg_id] == 0)

            # delta(j): number of racks spanned by local group G_j
            delta = model.addVars(ecl, vtype=GRB.INTEGER, name="delta")
            for lg_id in range(ecl):
                model.addConstr(delta[lg_id] == I_blk_lg.sum('*', lg_id))

            # m_cost_global_lg_tmp(i,j): tmp variable (as Gurobi doesn't
            # support multiplying consecutive three integers in one variable)
            m_cost_global_lg_tmp = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, name="m_cost_global_lg_tmp")
            for rack_id in range(max_num_racks):
                for lg_id in range(ecl):
                    model.addConstr(m_cost_global_lg_tmp[rack_id, lg_id] == I_alpha[rack_id, lg_id] * (1 - beta[rack_id, lg_id]))

            # m_cost_global_lg(i,j): representing the maintenance cost to
            # relate all the data blocks of local group G_j in rack R_i
            m_cost_global_lg = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, name="m_cost_global_lg")
            for rack_id in range(max_num_racks):
                for lg_id in range(ecl):
                    model.addConstr(m_cost_global_lg[rack_id, lg_id] == alpha[rack_id, lg_id] * (z - 1) + m_cost_global_lg_tmp[rack_id, lg_id] * (delta[lg_id] - z))

            # m_cost_global(i): maintenance cost of the data blocks in rack
            # R_i (global repair)
            m_cost_global = model.addVars(max_num_racks, vtype=GRB.INTEGER, name="m_cost_global")
            for rack_id in range(max_num_racks):
                model.addConstr(m_cost_global[rack_id] == m_cost_global_lg.sum(rack_id, '*'))

            # I_local(i): Indicator variable that whether the data blocks in
            # j-th local group can be locally repaired in the i-th rack. It
            # requires that alpha[rack_id, lg_id] >= 1
            I_local = model.addVars(max_num_racks, ecl, vtype=GRB.BINARY, name="I_local")
            for rack_id in range(max_num_racks):
                for lg_id in range(ecl):
                    model.addGenConstrIndicator(I_local[rack_id, lg_id], True, alpha[rack_id, lg_id] + beta[rack_id, lg_id] <= 1)
                    model.addGenConstrIndicator(I_local[rack_id, lg_id], False, alpha[rack_id, lg_id] + beta[rack_id, lg_id] >= 2)
            
            # m_cost(i,j): maintenance cost for the data block from local
            # group G_j in rack R_i (combining local and global repair)
            m_cost = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER,
            lb=0, ub=eck, name="m_cost")
            for rack_id in range(max_num_racks):
                for lg_id in range(ecl):
                    model.addConstr(m_cost[rack_id, lg_id] ==
                    (I_local[rack_id, lg_id] * (delta[lg_id] - 1) + (1 -
                    I_local[rack_id, lg_id]) * m_cost_global[rack_id]))

            # m_cost_sum(i,j): sum of maintenance costs for all the data
            # blocks for local group G_j in rack R_i
            m_cost_lg_sum = model.addVars(max_num_racks, ecl, vtype=GRB.INTEGER, lb=0, ub=eck, name="m_cost_lg_sum")
            for rack_id in range(max_num_racks):
                for lg_id in range(ecl):
                    model.addConstr(m_cost_lg_sum[rack_id, lg_id] == alpha[rack_id, lg_id] * m_cost[rack_id, lg_id])

            # AMC: average maintenance cost of the LRC stripe (continuous)
            AMC = model.addVar(vtype=GRB.CONTINUOUS, name="AMC")
            model.addConstr(AMC == m_cost_lg_sum.sum('*', '*') / eck)

            # Set objective
            model.setObjective(AMC, GRB.MINIMIZE)


            # Start from an initial solution (maintenance-robust-efficient deployment)
            for rack_id in range(max_num_racks):
                for lg_id in range(ecl):
                    alpha[rack_id, lg_id].Start = 0
                    beta[ecb, lg_id].Start = 0
                gamma[rack_id].Start = 0

            for lg_id in range(ecl):
                for rack_id in range(ecb):
                    alpha[rack_id, lg_id].Start = 1
                beta[ecb, lg_id].Start = 1
            gamma[ecb].Start = ecg

            #################################################################

        ############### Gurobi Parameter tuning ##############################
        
        model.setParam('MIPFocus', 3) # more focus on proving the objective bound
        model.setParam('Heuristics', 0) # only focus on proving the objective bound, instead of finding multiple feasible solutions

        ######################################################################


        # Optimize model
        model.optimize()

        # TODO: optimize the program and visualize the results

        for v in model.getVars():
            print(f"{v.VarName} {v.X:g}")

        print(f"Obj: {model.ObjVal:g}")


    except gp.GurobiError as e:
        print(f"Error code {e.errno}: {e}")
    # except AttributeError:
        # print("Encountered an attribute error")



if __name__ == '__main__':
    main()