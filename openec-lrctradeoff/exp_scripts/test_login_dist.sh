#!/usr/bin/expect -f
# usage: test ssh connection on all nodes

source "./config.sh"

for idx in $(seq 0 $((num_nodes-1))); do
    ip=${ip_list[$idx]}
    user=${user_list[$idx]}
    passwd=${passwd_list[$idx]}
    
    expect << EOF
    
    set timeout 5
    spawn ssh $user@$ip "echo success"
    expect {
        "*yes/no" { send "yes\n"; exp_continue }
        "*password" { send "$passwd\n" }
    }
     
EOF
done
