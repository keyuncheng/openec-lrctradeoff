import os
import time
import sys
import json
import argparse
import sys
import subprocess
from pathlib import Path
import numpy as np
import math
import configparser

# Run this script on the NameNode (Controller)
user_name = "kycheng"
user_passwd = "kycheng"

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

def get_eval_code_names(exp):
    # code name
    eval_code_name_repair = ""
    eval_code_name_maintenance = ""
    if exp.approach == "flat":
        eval_code_name_repair += "AF"
        eval_code_name_maintenance += "AF"
    elif exp.approach == "tradeoff":
        eval_code_name_repair += "AT"
        eval_code_name_maintenance += "AT"
    elif exp.approach == "optr":
        eval_code_name_repair += "AOR"
        eval_code_name_maintenance += "AOR"
    elif exp.approach == "optm":
        eval_code_name_repair += "AOM"
        eval_code_name_maintenance += "AOM"
    eval_code_name_repair += "_{}_{}".format(str(exp.eck + exp.ecl + exp.ecg), str(exp.eck))
    eval_code_name_maintenance += "_{}_{}".format(str(exp.eck + exp.ecl + exp.ecg), str(exp.eck))
    if exp.approach == "tradeoff":
        eval_code_name_repair += "_{}_r".format(str(exp.eta))
        eval_code_name_maintenance += "_{}_m".format(str(exp.eta))

    return eval_code_name_repair, eval_code_name_maintenance

def find_block_id_and_ip(stripe_name, block_id):
    oec_block_name = "/{}_oecobj_{}".format(stripe_name, block_id)
    find_node_ip_and_block_cmd = "hdfs fsck {} -files -blocks -locations | grep Datanode".format(oec_block_name)
    
    find_ip_result = exec_cmd(find_node_ip_and_block_cmd, exec=False)

    node_ip = "undefined_ip"
    block_name = "blk_undefined"

    try:
        find_ip_result.index("blk_")
    except ValueError:
        print("oec_object {} not found in HDFS!".format(oec_block_name))
        return node_ip, block_name

    block_begin = find_ip_result.index("blk_") + len("blk_")
    block_end = find_ip_result.index("len=")
    block_meta = find_ip_result[block_begin:block_end]
    block_split = block_meta.split("_")
    block_name = block_split[0]

    ip_begin = find_ip_result.index("WithStorage[") + len("WithStorage[")
    ip_end = find_ip_result.index(",DS")
    ip_origin = find_ip_result[ip_begin:ip_end]
    ip_split = ip_origin.split(":")
    node_ip = ip_split[0]
    print("found block for stripe_name: {}: {} {}", oec_block_name, node_ip, block_name)
    return node_ip, block_name

def delete_node_block(hdfs_dir, node_ip, block_name = "*"):
    print("Start to delete block: " + node_ip + ", block: " + block_name)
    delete_cmd = "ssh " + node_ip + " \"cd {}/dfs/data/current/BP-*/current/finalized/subdir0/subdir0/ && rm {}\"".format(hdfs_dir, block_name)
    exec_cmd(delete_cmd, exec=False)

    time.sleep(2)
    print("Delete block finished: " + node_ip + ", block: " + block_name)

def check_hdfs_blocks():
    hdfs_check_blocks_cmd="hdfs fsck -list-corruptfileblocks"
    ret_val = exec_cmd(hdfs_check_blocks_cmd, exec=False)
    print(ret_val)


def read_file_block(filename, num_runs):
    print("Start to read file {} for {} runs".format(filename, num_runs))

    read_time_list = []
    for i in range(num_runs):
        read_cmd = "./OECClient read {} {}".format("/" + filename, filename)
        ret_val = exec_cmd(read_cmd, exec=False)

        read_time = -1

        try:
            ret_val.index("duration:")
        except ValueError:
            print("Error reading object {}".format(filename))
            continue

        begin_p = ret_val.index("duration:") + len("duration:") + 1
        end_p = ret_val.index("\n")

        if end_p - begin_p <= 0:
            print("Error: read file failed")
        else:
            read_time = float(ret_val[begin_p:end_p])

        read_time_list.append(read_time)
        time.sleep(1)
    return read_time_list


def main():
    args = parse_args(sys.argv[1:])
    if not args:
        exit()

    start_exp_time = time.time()

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
    exp.in_bw_Kbps = int(exp.in_bw_Kbps)
    exp.cr_bw_Kbps = int(exp.cr_bw_Kbps)
    exp.num_runs = int(exp.num_runs)

    # cluster settings
    configs.Cluster = DictToObject(configs.Cluster)
    cluster = configs.Cluster
    cluster.controller_id = int(cluster.controller_id)
    cluster.gateway_id = int(cluster.gateway_id)
    cluster.agent_ids = list(map(int, cluster.agent_ids.split(',')))
    # load nodes
    cluster.nodes=[]
    with open(cluster.login_file, 'r') as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                continue
            # format: ip, username, password
            elements = line.strip().split(' ')
            cluster.nodes.append(elements)
    cluster.num_nodes=len(cluster.nodes)

    print("Configurations:")
    print(vars(exp))
    print(vars(cluster))

    eval_code_name_repair, eval_code_name_maintenance = get_eval_code_names(exp)

    print("eval_code_names: {}, {}".format(eval_code_name_repair, eval_code_name_maintenance))

    oec_dir = "{}/openec-lrctradeoff".format(cluster.proj_dir)
    exp_script_dir = "{}/exp_scripts".format(oec_dir)

    print(*cluster.agent_ids)

    # set network topology
    cmd = "cd {} && python3 export_topology.py -oec_code_name {} -dn_ids {}".format(exp_script_dir, eval_code_name_repair, ' '.join(str(item) for item in cluster.agent_ids))
    exec_cmd(cmd, exec=False)

    # update configurations
    cmd = "cd {} && bash update_configs_dist.sh {} {}".format(exp_script_dir, exp.block_size_byte, exp.pkt_size_byte)
    exec_cmd(cmd, exec=False)

    for block_id in range(exp.eck):
        print("Start evaluation for code {} and {} block {}".format(eval_code_name_repair, eval_code_name_maintenance, block_id))

        # restart hdfs and openec
        cmd = "cd {} && bash restart_oec.sh".format(exp_script_dir)
        exec_cmd(cmd, exec=False)

        time.sleep(1)

        agent_id = cluster.agent_ids[block_id]
        agent_ip = cluster.nodes[agent_id][0]

        # data block name
        block_size_MiB = int(exp.block_size_byte / 1024 / 1024)
        input_data_size_MiB = block_size_MiB * exp.eck
        input_data_filename = "{}/{}MiB".format(cluster.proj_dir, input_data_size_MiB)
        # generate data block
        if os.path.isfile(input_data_filename):
            print("data block exists: {}".format(input_data_filename))
        else:
            print("data block not exists: {}; generate".format(input_data_filename))
            cmd = "ssh {}@{} \"dd if=/dev/urandom of={} bs={}MiB count={} iflag=fullblock\"".format(user_name, agent_ip, input_data_filename, block_size_MiB, exp.eck)
            exec_cmd(cmd, exec=False)

        stripe_name_repair = "repair_" + eval_code_name_repair
        stripe_name_maintenance = "maintenance_" + eval_code_name_maintenance

        # write stripe to hdfs on the node storing block id
        cmd = "ssh {}@{} \"cd {} && ./OECClient write {} {} {} online {}\"".format(user_name, agent_ip, oec_dir, input_data_filename, "/" + stripe_name_repair, eval_code_name_repair, input_data_size_MiB)
        exec_cmd(cmd, exec=False)
        time.sleep(1)

        cmd = "ssh {}@{} \"cd {} && ./OECClient write {} {} {} online {}\"".format(user_name, agent_ip, oec_dir, input_data_filename, "/" + stripe_name_maintenance, eval_code_name_maintenance, input_data_size_MiB)
        exec_cmd(cmd, exec=False)
        time.sleep(1)

        # delete node block

        # repair
        node_ip, block_name = find_block_id_and_ip(stripe_name_repair, block_id)
        delete_node_block(cluster.hdfs_dir, node_ip, block_name)

        # maintenance
        node_ip, block_name = find_block_id_and_ip(stripe_name_maintenance, block_id)
        delete_node_block(cluster.hdfs_dir, node_ip, block_name)

        time.sleep(3)
        check_hdfs_blocks()

        # set cross-rack bandwidth
        cmd = "cd {} && python3 set_topology_cluster.py -option set -cr_bw {} -gw_ip {}".format(exp_script_dir, exp.cr_bw_Kbps, cluster.nodes[cluster.gateway_id][0])
        exec_cmd(cmd, exec=False)

        # degraded read file
        read_filename_repair = "{}_{}".format(stripe_name_repair, block_id)
        read_repair_time_list = read_file_block(read_filename_repair, exp.num_runs)

        read_filename_maintenance = "{}_{}".format(stripe_name_maintenance, block_id)
        read_maintenance_time_list = read_file_block(read_filename_maintenance, exp.num_runs)

        # save results
        result_save_foler_repair = "{}/eval_results/{}/".format(cluster.proj_dir, eval_code_name_repair)
        os.makedirs(result_save_foler_repair, exist_ok=True)
        result_save_path = result_save_foler_repair + "result.json"
        # with open(result_save_path, 'w',encoding='utf8') as f:
        #     f.write(" ".join(str(item) for item in read_repair_time_list) +
        #     "\n")
        
        print("save {} result in {}".format(eval_code_name_repair, result_save_path))

        result_save_foler_maintenance = "{}/eval_results/{}/".format(cluster.proj_dir, eval_code_name_maintenance)
        os.makedirs(result_save_foler_maintenance, exist_ok=True)
        result_save_path = result_save_foler_maintenance + "result.json"
        # with open(result_save_path, 'w',encoding='utf8') as f:
        #     f.write(" ".join(str(item) for item in
        #     read_maintenance_time_list) + "\n")
        
        print("save {} result in {}".format(eval_code_name_repair, result_save_path))

        # clear cross-rack bandwidth
        cmd = "cd {} && python3 set_topology_cluster.py -option clear -cr_bw {} -gw_ip {}".format(exp_script_dir, exp.cr_bw_Kbps, cluster.nodes[cluster.gateway_id][0])
        exec_cmd(cmd, exec=False)

        print("Finished evaluation for code {} and {} block {}".format(eval_code_name_repair, eval_code_name_maintenance, block_id))

    end_exp_time = time.time()
    print("Evaluation on code {} and {} finished, used time: {} (s)".format(eval_code_name_repair, eval_code_name_maintenance, str(end_exp_time - start_exp_time)))

if __name__ == '__main__':
    main()