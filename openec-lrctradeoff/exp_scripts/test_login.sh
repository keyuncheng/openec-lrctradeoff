#!/usr/bin/expect -f

# test ssh connection

login_file="/home/kycheng/scripts/login.txt"
echo "login_file:" $login_file

while IFS= read -r line
do
    ip=`echo $line | cut -d " " -f 1`
    user=`echo $line | cut -d " " -f 2`
    passwd=`echo $line | cut -d " " -f 3`
    expect <<EOF
    set timeout 5
    spawn ssh $user@$ip "echo success"
    expect {
        "*yes/no" { send "yes\n"; exp_continue }
        "*password" { send "$passwd\n" }
    }
    send "exit\n"
    expect eof
EOF
done < $login_file
