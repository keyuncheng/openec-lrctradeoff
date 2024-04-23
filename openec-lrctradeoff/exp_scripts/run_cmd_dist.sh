#!/bin/bash

if [ "$#" != "1" ]; then
	echo "Usage: $0 <script>.sh" >&2
    exit 1
fi

cur_dir=`pwd`
script=$1

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
   
    # run cmd
    echo ssh -n $user@$ip "echo kycheng | sudo -S apt-get -y install expect"
    ssh -n $user@$ip "echo kycheng | sudo -S apt-get -y install expect"

done < $login_file
