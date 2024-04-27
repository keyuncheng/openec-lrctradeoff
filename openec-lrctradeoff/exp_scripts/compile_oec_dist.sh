#!/usr/bin/expect -f
# usage: set login for all nodes

home_dir=$(echo ~)
proj_dir=$home_dir/widelr
coec_dir=$proj_dir/openec-lrctradeoff

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
    set timeout -1
    send "cd $oec_dir && rm -rf CMakeCache.txt && rm -rf CMakeFiles/ && cmake . -DFS_TYPE:STRING=HDFS3 && make"
    expect eof

    set timeout 1
    send "exit\n"
    expect eof

EOF
done

