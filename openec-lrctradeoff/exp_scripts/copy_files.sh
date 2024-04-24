#!/usr/bin/bash
# usage: copy file/dir to all nodes

if [ "$#" != "1" ]; then
    echo "Usage: $0 file/dir" >&2
    exit 1
fi

source "./config.sh"

file=$1

# copy file/dir
for idx in $(seq 0 $((num_nodes-1))); do
    ip=${ip_list[$idx]}
    user=${user_list[$idx]}
    passwd=${passwd_list[$idx]}
    
    rsync -av $file $user@$ip:$file
done