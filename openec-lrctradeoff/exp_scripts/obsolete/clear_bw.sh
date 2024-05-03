#!/bin/bash
# usage: clear bandwidth setting

cur_ip=$(ifconfig | grep '192.168.0' | head -1 | sed "s/ *inet [addr:]*\([^ ]*\).*/\1/")
cur_dev=$(ifconfig | grep -B1 $cur_ip | grep -o "^\w*")

tc filter del dev $cur_dev > /dev/null 2>&1
tc qdisc del dev $cur_dev root > /dev/null 2>&1

echo disable bandwidth setting [ $cur_ip $cur_dev ]