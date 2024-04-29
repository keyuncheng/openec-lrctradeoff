#!/bin/bash
# usage: set bandwidth to <bw mbps>

if [ "$#" != "2" ]; then
	echo "Usage: $0 dst_ip bandwidth (Mbps)" >&2
    exit 1
fi

dst_ip=$1
bandwidth=$2
bandwidth_upper=1000

cur_ip=$(ifconfig | grep '192.168.0' | head -1 | sed "s/ *inet [addr:]*\([^ ]*\).*/\1/")
cur_dev=$(ifconfig | grep -B1 $cur_ip | grep -o "^\w*")

tc qdisc del dev $cur_dev root > /dev/null 2>&1
tc qdisc add dev $cur_dev root handle 1: htb default 20
tc class add dev $cur_dev parent 1: classid 1:1 htb rate ${bandwidth}mbit ceil ${bandwidth}mbit
tc class add dev $cur_dev parent 1: classid 1:20 htb rate ${bandwidth_upper}mbit

tc filter add dev $cur_dev protocol ip parent 1: prio 0 u32 match ip dst $dst_ip flowid 1:1

echo enable bandwidth setting [ $cur_ip $cur_dev to $dst_ip: $bandwidth Mbps]