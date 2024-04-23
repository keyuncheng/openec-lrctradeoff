#!/bin/bash

if [ "$#" -lt "1" ]; then
	echo "Usage: $0 <script>.sh <args>" >&2
    exit 1
fi

cur_dir=`pwd`
script=$1
args=${@:2}

if [ ! -f "$cur_dir/$script" ]; then
    echo "script $script does not exist"
    exit 1
fi

login_file="/home/kycheng/scripts/login.txt"
echo "login_file:" $login_file

while IFS= read -r line
do
    ip=`echo $line | cut -d " " -f 1`
    user=`echo $line | cut -d " " -f 2`
    passwd=`echo $line | cut -d " " -f 3`
   
    # run script
    echo ssh -n $user@$ip "cd $cur_dir && bash $script $args"
    ssh -n $user@$ip "cd $cur_dir && bash $script $args"

done < $login_file
