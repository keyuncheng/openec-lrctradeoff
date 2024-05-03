#!/bin/bash
# usage: set bandwidth to <bw mbps>

if [ "$#" != "1" ]; then
	echo "Usage: $0 bandwidth (Mbps)" >&2
    exit 1
fi

bandwidth=$1
bandwidth_upper=1000

cur_ip=$(ifconfig | grep '192.168.10' | head -1 | sed "s/ *inet [addr:]*\([^ ]*\).*/\1/")
cur_dev=$(ifconfig | grep -B1 $cur_ip | grep -o "^\w*")

# main class
tc qdisc add dev $cur_dev root handle 1: htb default 10
# tc class add dev $cur_dev parent 1: classid 1:1 htb rate ${bandwidth_upper}mbit ceil ${bandwidth_upper}mbit burst 10mb
# 
# # subclass for cross-rack and inner rack
# tc class add dev $cur_dev parent 1:1 classid 1:10 htb rate ${bandwidth}mbit burst 10mb
# tc class add dev $cur_dev parent 1:1 classid 1:20 htb rate ${bandwidth_upper}mbit ceil ${bandwidth_upper}mbit burst 10mb
# 
# tc qdisc add dev $cur_dev parent 1:10 handle 10: sfq perturb 10  
# tc qdisc add dev $cur_dev parent 1:20 handle 20: sfq perturb 10



tc class add dev $cur_dev parent 1: classid 1:1 htb rate ${bandwidth}mbit ceil ${bandwidth}mbit burst 1000k

echo initialize bandwidth setting [ $cur_ip $cur_dev $bandwidth Mbps]
