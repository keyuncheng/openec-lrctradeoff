#!/usr/bin/bash
# usage: configuration files

root_user_name=kycheng
root_user_passwd=kycheng
# login_file="/home/kycheng/scripts/login.txt"
login_file="/mnt/e/projects/wide-lrc/widelrc/openec-lrctradeoff/exp_scripts/login.txt"

# get node list
ip_list=()
user_list=()
passwd_list=()

while IFS= read -r line
do
    ip=`echo $line | cut -d " " -f 1`
    user=`echo $line | cut -d " " -f 2`
    passwd=`echo $line | cut -d " " -f 3`
    
    ip_list+=($ip)
    user_list+=($user)
    passwd_list+=($passwd)
done < $login_file

num_nodes=${#ip_list[@]}

# print configs
echo "login_file:" $login_file
echo Number of nodes: $num_nodes

for idx in $(seq 0 $((num_nodes-1))); do
    echo Node $idx: ${ip_list[$idx]} ${user_list[$idx]} ${passwd_list[$idx]}
done