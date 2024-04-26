#!/usr/bin/expect -f
# usage: set login for all nodes

source "./config.sh"

for idx in $(seq 0 $((num_nodes-1))); do
    ip=${ip_list[$idx]}
    user=${user_list[$idx]}
    passwd=${passwd_list[$idx]}
    
    expect << EOF
   
    # ssh 
    set timeout 5
    spawn ssh -t $root_user_name@$ip 
    expect {
        "*yes/no" { send "yes\n"; exp_continue }
        "*password" { send "$root_user_passwd\n"; exp_continue }
    }

    # adduser
    set timeout 5
    send "sudo adduser $user\n" 
    expect {
        "*already exists" {exit 0}
        "*password for" {send "$root_user_passwd\n"; exp_continue}
        "*New password" {send "$passwd\n"; exp_continue}
        "*Retype new password" {send "$passwd\n"; exp_continue}
        "*Full Name" {send "\n"; exp_continue}
        "*Room Number" {send "\n"; exp_continue}
        "*Work Phone" {send "\n"; exp_continue}
        "*Home Phone" {send "\n"; exp_continue}
        "*Other" {send "\n"; exp_continue}
        "*correct?" {send "Y\n"; exp_continue}
    }
    
    # add sudo privilege
    set timeout 1
    send "sudo usermod -aG sudo $user\n"

    set timeout 1
    send "exit\n"
    expect eof

EOF
done

