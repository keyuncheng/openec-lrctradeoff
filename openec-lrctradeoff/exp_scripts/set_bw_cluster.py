#!/usr/bin/env python3
import argparse
import sys
import subprocess
from pathlib import Path
from collections import OrderedDict

home_dir = str(Path.home())
oec_dir = "{}/widelrc/openec-lrctradeoff".format(home_dir)
exp_scripts_dir = "{}/exp_scripts".format(oec_dir)
hdfs_dir = "{}/hadoop-3.3.4".format(home_dir)
hdfs_config = "rack_topology.data"
clear_bw_script = "clear_bw.sh"
init_bw_script = "init_bw.sh"
set_bw_script = "set_bw.sh"
user_name = "kycheng"
user_passwd = "kycheng"

def parse_args(cmd_args):
    arg_parser = argparse.ArgumentParser(description="set bandwidth for the cluster (based on HDFS rack topology).")

    # input parameters
    arg_parser.add_argument("-option", type=str, required=True, help="option for bandwidth settings (set/clear)")
    arg_parser.add_argument("-cr_bw", type=int, required=True, help="cross-rack bandwidth (Mbps)")
    
    
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


def main():
    args = parse_args(sys.argv[1:])
    if not args:
        exit()

    # input parameters
    option = args.option
    cr_bw = args.cr_bw

    # read rack topology file from hdfs
    node_to_rack = OrderedDict()
    rack_to_node = OrderedDict()
    hdfs_config_path = "{}/etc/hadoop/{}".format(hdfs_dir, hdfs_config)
    with open(hdfs_config_path, "r") as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                continue
            arr = line.strip().split(' ')
            node_ip = arr[0]
            rack_id = int(arr[1])
            node_to_rack[node_ip] = rack_id
            rack_to_node[rack_id] = rack_to_node.get(rack_id, []) + [node_ip]

    for cur_node_ip, cur_rack_id in node_to_rack.items():
        if option == "clear":
            print("clear bandwidth for node {} (rack {})".format(cur_node_ip, cur_rack_id))
            cmd = "ssh {}@{} \"cd {} && echo {} | sudo -S bash {}\"".format(user_name, cur_node_ip, exp_scripts_dir, user_passwd, clear_bw_script)
            exec_cmd(cmd, exec=True)
        elif option == "set":
            print("set bandwidth for node {} (rack {})".format(cur_node_ip, cur_rack_id))
            cmd = "ssh {}@{} \"cd {} && echo {} | sudo -S bash {} {}\"".format(user_name, cur_node_ip, exp_scripts_dir, user_passwd, init_bw_script, cr_bw)
            exec_cmd(cmd, exec=True)

            for node_ip, rack_id in node_to_rack.items():
                if cur_node_ip == node_ip:
                    continue
                # need to set inner-rack bandwidth
                if cur_rack_id == rack_id:
                    cmd = "ssh {}@{} \"cd {} && echo {} | sudo -S bash {} {} {}\"".format(user_name, cur_node_ip, exp_scripts_dir, user_passwd, set_bw_script, node_ip, cr_bw)
                    exec_cmd(cmd, exec=True)
        else:
            print("unknown option: {}".format(option))
            break

    print("Finished setting up bandwidth for cluster")

if __name__ == '__main__':
    main()
