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

    running_time_token = "generating"

    # baselines
    baselines = ["RDPM", "BWPM", "BTPM"]
    baseline_results = {
        "RDPM": {
            "running_time": []
        },
        "BWPM": {
            "running_time": []
        },
        "BTPM": {
            "running_time": []
        }
    }
    baseline_cnter = 0

    with open(log_path, "r") as f:
        for line in f.readlines():
            if running_time_token in line:
                match = re.search(r"finished generating solution, time: (\d+.\d+)", line)
                if not match.groups():
                    print("Error: cannot find running_time")
                    exit()
                running_time = float(match.group(1))

                # append results
                baseline_results[baselines[baseline_cnter]]["running_time"].append(running_time)

                # increment results
                baseline_cnter = (baseline_cnter + 1) % len(baselines)

    # print results
    print(baseline_results)

    for bl_name, bl_result in baseline_results.items():
        # get results under student's t-dist
        bl_result["running_time"] = student_t_dist(bl_result["running_time"])

        # polish (mean, lower, upper)
        bl_result["running_time"] = bl_result["running_time"][0], bl_result["running_time"][0] + bl_result["running_time"][1], bl_result["running_time"][0] - bl_result["running_time"][1]

        # polish (max_load to second)
        bl_result["running_time"] = [item * 1.0 / 1000 for item in bl_result["running_time"]]

    # print results
    print(baseline_results)


    
if __name__ == '__main__':
    main()
