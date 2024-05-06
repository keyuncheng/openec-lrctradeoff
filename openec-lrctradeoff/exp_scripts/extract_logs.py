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



def max_load_to_second(max_load, block_size_MiB=64):
    return max_load * (block_size_MiB * 1024 * 1024 * 8) / (10 ** 6)

def main():
    args = parse_args(sys.argv[1:])
    if not args:
        exit()

    # read bandwidth
    log_filename = args.log_filename 

    print("log_filename: {}".format(log_filename))

    log_path = Path(log_filename).resolve()

    result_token = "result for code"

    code_class_name = ""

    results = {}

    with open(log_filename, "r") as f:
    # with open(log_path, "r") as f:
        for line in f.readlines():
            if result_token in line:
                match = re.search(r"{} ([A-Za-z_0-9]+) block (\d+): (.*)".format(result_token), line)
                if not match.groups():
                    print("Error: cannot find result")
                    exit()
                code_class_name = match.group(1)
                block_id = int(match.group(2))
                results_raw = match.group(3)

                results_blk = [float(item) for item in results_raw.split(" ")]

                if code_class_name not in results:
                    results[code_class_name] = {}

                results[code_class_name][block_id] = results_blk

    for code_class_name, results_code_class in results.items():
        num_runs = len(results_code_class[0])
        num_blks = len(results_code_class)
        avg_blks = []
        for i in range(num_runs):
            avg_blks.append(sum([results_code_class[j][i] for j in range(num_blks)]) / num_blks)
        # print(avg_blks)

        results_std_t = student_t_dist(avg_blks)
        results_avg = results_std_t[0]
        results_upper = results_std_t[0] + results_std_t[1]
        results_lower = results_std_t[0] - results_std_t[1]

        # print("raw_results for {}: {}".format(code_class_name, results))
        print(code_class_name, results_avg, results_upper, results_lower)
    
if __name__ == '__main__':
    main()
