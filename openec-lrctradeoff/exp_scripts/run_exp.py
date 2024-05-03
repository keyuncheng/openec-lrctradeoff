#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
from pathlib import Path
import numpy as np
import math
import configparser

def parse_args(cmd_args):
    arg_parser = argparse.ArgumentParser(description="run experiment") 

    # Input parameters: exp_settings_file
    arg_parser.add_argument("-exp_settings_file", type=str, required=True, help="experiment settings file (.ini)")
    
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

class MyConfigParser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)

def main():
    args = parse_args(sys.argv[1:])
    if not args:
        exit()

    # Input parameters: exp_settings_file
    exp_settings_file = args.exp_settings_file

    # 0. Load configurations
    configs_raw = MyConfigParser()
    configs_raw.read(exp_settings_file)

    # 0.1 parse configurations
    configs = DictToObject({section: dict(configs_raw[section]) for section in configs_raw.sections()})

    # experiments
    configs.Experiment = DictToObject(configs.Experiment)
    exp = configs.Experiment
    exp.eck = int(exp.eck)
    exp.ecl = int(exp.ecl)
    exp.ecg = int(exp.ecg)
    exp.eta = int(exp.eta)
    exp.block_size_byte = int(exp.block_size_byte)
    exp.pkt_size_byte = int(exp.pkt_size_byte)
    exp.in_bw_Mbps = int(exp.in_bw_Mbps)
    exp.cr_bw_Mbps = int(exp.cr_bw_Mbps)
    exp.num_runs = int(exp.num_runs)

    # cluster settings
    configs.Cluster = DictToObject(configs.Cluster)
    cluster = configs.Cluster
    cluster.controller_id = int(cluster.controller_id)
    cluster.agent_ids = list(map(int, cluster.agent_ids.split(',')))
    # load nodes
    cluster.nodes=[]
    with open(cluster.login_file, 'r') as f:
        for line in f.readlines():
            # format: ip, username, password
            elements = line.strip().split(' ')
            cluster.nodes.append(elements)
    cluster.num_nodes=len(cluster.nodes)

    # check parameters
    if check_params(configs) == False:
        return

    print("Configurations:")
    print(vars(exp))
    print(vars(cluster))

    # # load rack configurations
    # # get rack configurations from PlacementTest
    # exp.racks = []
    # code_name=""
    # if exp.approach == "flat":
    #     code_name = "AzureLRCFlat_{}_{}".format(exp.eck + exp.ecn + exp.ecg, exp.eck)
    # elif exp.approach == "tradeoff":
    #     code_name = "AzureLRCTradeoff_{}_{}_{}".format(exp.eck + exp.ecn + exp.ecg, exp.eck, exp.eta)
    # elif exp.approach == "optm":
    #     code_name = "AzureLRCOptM_{}_{}".format(exp.eck + exp.ecn + exp.ecg, exp.eck)
    # else:
    #     print("Error: Invalid approach")
    #     return
    
    # # check if code_name exists in configuration file
    # cmd = "grep -Fxq {} {}".format(code_name, "{}/conf/sysSetting.xml".format(exp.proj_dir))
    # ret_msg = exec_cmd(cmd)
    # print(ret_msg)


    # 1. Update HDFS configs

    # 1.1 block size
    # 1.2 packet size
    # 1.3 cluster settings

    # Update OpenEC configs
    
    # 2.1 block size
    # 2.2 packet size
    # 2.3 EC configurations
    # 2.4 cluster settings

    # Update bandwidth settings
    

if __name__ == '__main__':
    main()