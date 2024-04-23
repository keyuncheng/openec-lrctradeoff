#!/usr/bin/expect -f

# set login by root user

root_user_name=kycheng
root_user_passwd=kycheng
login_file="/home/kycheng/scripts/login.txt"
echo "login_file:" $login_file

while IFS= read -r line
do
    ip=`echo $line | cut -d " " -f 1`
    user=`echo $line | cut -d " " -f 2`
    passwd=`echo $line | cut -d " " -f 3`
    expect <<EOF
   
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
    set timeout 2
    send "sudo usermod -aG sudo $user\n"
    
    send "exit\n"
    expect eof
EOF
done < $login_file
