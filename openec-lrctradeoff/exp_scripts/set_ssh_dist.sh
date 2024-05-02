#!/usr/bin/expect -f
# usage: set mutual password-less ssh connection on all nodes

source "./config.sh"

# create id_rsa
if [ ! -f ~/.ssh/id_rsa ];then
	 ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa
 else
	  echo "id_rsa has created ..."
fi

for idx in $(seq 0 $((num_nodes-1))); do
    ip=${ip_list[$idx]}
    user=${user_list[$idx]}
    passwd=${passwd_list[$idx]}
    
    expect << EOF

    # remove key
    set timeout 2
    spawn ssh-keygen -f "/home/$user/.ssh/known_hosts" -R $ip
    expect eof

    # set ssh-copy-id 
    set timeout 2
    spawn ssh-copy-id -f $user@$ip
    expect {
        "*yes/no" { send "yes\n"; exp_continue }
        "*password" { send "$passwd\n"; exp_continue }
    }

EOF
done
