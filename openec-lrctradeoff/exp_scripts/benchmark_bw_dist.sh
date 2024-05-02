#!/bin/bash
# usage: test bandwidth between current node and all nodes

source "./config.sh"

cur_ip=$(ifconfig | grep '192.168.10' | head -1 | sed "s/ *inet [addr:]*\([^ ]*\).*/\1/")

iperf -s &

for idx in $(seq 0 $((num_nodes-1))); do
    ip=${ip_list[$idx]}
    user=${user_list[$idx]}
    passwd=${passwd_list[$idx]}

    echo Current Node: ${cur_ip}
    
    ssh $user@$ip iperf -c ${cur_ip}
done

killall iperf
