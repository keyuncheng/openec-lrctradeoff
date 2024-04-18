import os
import sys
import subprocess
import argparse
import time
import random
import numpy as np
from pathlib import Path
import numpy as np
from scipy.stats import t
import re

def parse_args(cmd_args):
    arg_parser = argparse.ArgumentParser(description="extract logs and generate data script") 
    arg_parser.add_argument("-log_filename", type=str, required=True, help="log filename")
    
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

def student_t_dist(samples_arr, ci=0.95):
    samples = np.array(samples_arr)
    # sample mean
    mean = samples.mean()
    # sample standard deviation
    stdev = samples.std()
    # degree of freedom = # of samples - 1
    dof = len(samples) - 1
    # t value
    t_crit = np.abs(t.ppf((1-ci) / 2, dof))
    print('t = {:.3f} when percentage = {:.3f} and degree of freedom = {:d}'.format(t_crit, (1-ci)*100/2, dof))
    # interval
    t_diff = stdev * t_crit / np.sqrt(len(samples))

    return mean, t_diff


def main():
    args = parse_args(sys.argv[1:])
    if not args:
        exit()

    # read bandwidth
    log_filename = args.log_filename 

    print("log_filename: {}".format(log_filename))

    log_path = Path(log_filename).resolve()

    iter_token = "end iteration"
    finished_iter_token = "finished optimization"

    # baselines
    baselines = ["BTPM"]
    baseline_results = {
        "BTPM": {
            "iter": []
        }
    }
    baseline_cnter = 0

    with open(log_path, "r") as f:
        iter = None
        for line in f.readlines():
            if finished_iter_token in line:
                # append results
                baseline_results[baselines[baseline_cnter]]["iter"].append(iter + 2)

                # increment results
                baseline_cnter = (baseline_cnter + 1) % len(baselines)

            if iter_token in line:
                match = re.search(r"end iteration: (\d+)\,.*", line)
                if not match or not match.groups():
                    print("Error: cannot find iter")
                    exit()
                # print(line)
                iter = int(match.group(1))

                

    # print results
    print(baseline_results)

    for bl_name, bl_result in baseline_results.items():
        # get results under student's t-dist
        bl_result["iter"] = student_t_dist(bl_result["iter"])

        # polish (mean, lower, upper)
        bl_result["iter"] = bl_result["iter"][0], bl_result["iter"][0] + bl_result["iter"][1], bl_result["iter"][0] - bl_result["iter"][1]

        # polish (max_load to second)
        # bl_result["iter"] = [item * 1.0 / 1000 for item in bl_result["iter"]]

    # print results
    print(baseline_results)


    
if __name__ == '__main__':
    main()
