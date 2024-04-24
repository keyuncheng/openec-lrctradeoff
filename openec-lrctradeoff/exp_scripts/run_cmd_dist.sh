#!/bin/bash
# usage: run command on all nodes

if [ "$#" != "1" ]; then
	echo "Usage: $0 <script>.sh" >&2
    exit 1
fi

source "./config.sh"

cur_dir=`pwd`
script=$1

if [ ! -f "$cur_dir/$script" ]; then
    echo "script $script does not exist"
    exit 1
fi

# execute command
for idx in $(seq 0 $((num_nodes-1))); do
    ip=${ip_list[$idx]}
    user=${user_list[$idx]}
    passwd=${passwd_list[$idx]}
    
    # echo ssh -n $user@$ip "echo kycheng | sudo -S apt-get -y install expect"
    # ssh -n $user@$ip "echo kycheng | sudo -S apt-get -y install expect"
    echo "\$nrconf{restart} = 'a'" | sudo tee /etc/needrestart/conf.d/no-prompt.conf
done
