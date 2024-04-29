#!/bin/bash
# usage: set bandwidth to <bw mbps>

if [ "$#" != "1" ]; then
	echo "Usage: $0 bandwidth (Mbps)" >&2
    exit 1
fi

bandwidth=$1
bandwidth_upper=1000

cur_ip=$(ifconfig | grep '192.168.0' | head -1 | sed "s/ *inet [addr:]*\([^ ]*\).*/\1/")
cur_dev=$(ifconfig | grep -B1 $cur_ip | grep -o "^\w*")

tc qdisc add dev $cur_dev root handle 1: htb default 20
tc class add dev $cur_dev parent 1: classid 1:1 htb rate ${bandwidth}mbit ceil ${bandwidth}mbit
tc class add dev $cur_dev parent 1: classid 1:20 htb rate ${bandwidth_upper}mbit

echo initialize bandwidth setting [ $cur_ip $cur_dev $bandwidth Mbps]