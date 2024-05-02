#!/bin/bash
# usage: set bandwidth to <bw mbps>
# must call init_bw.sh first to initialize the setting

if [ "$#" != "2" ]; then
	echo "Usage: $0 dst_ip bandwidth (Mbps)" >&2
    exit 1
fi

dst_ip=$1
bandwidth=$2
bandwidth_upper=1000

cur_ip=$(ifconfig | grep '192.168.10' | head -1 | sed "s/ *inet [addr:]*\([^ ]*\).*/\1/")
cur_dev=$(ifconfig | grep -B1 $cur_ip | grep -o "^\w*")

# tc filter add dev $cur_dev protocol ip parent 1:0 prio 1 u32 match ip dst $dst_ip flowid 1:20
tc filter add dev $cur_dev protocol ip parent 1: prio 7 u32 match ip dst $dst_ip flowid 1:1

echo enable bandwidth setting [ $cur_ip $cur_dev to $dst_ip: $bandwidth Mbps]
