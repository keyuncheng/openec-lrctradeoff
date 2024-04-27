#!/bin/bash

source "./config.sh"

home_dir=$(echo ~)
proj_dir=${home_dir}/widelrc/openec-lrctradeoff
oec_script_dir=${proj_dir}/script
exp_scripts_dir=${proj_dir}/exp_scripts

# stop OEC
cd ${oec_script_dir}
python2.7 stop.py

# clear metadata
cd ${proj_dir}
rm -f coor_output
rm -f entryStore
rm -f poolStore

# clear logs
rm -f coor_output
for idx in $(seq 0 $((num_nodes-1))); do
    ip=${ip_list[$idx]}
    user=${user_list[$idx]}
    passwd=${passwd_list[$idx]}
    
    ssh -n $user@$ip "cd ${proj_dir}; rm -f agent_output"
done

# restart HDFS
cd ${scripts_exp_dir}
bash restart_hdfs.sh

sleep 2

cd ${script_dir}
bash env.sh && python2.7 start.py
