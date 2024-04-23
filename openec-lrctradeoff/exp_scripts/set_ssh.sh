#!/usr/bin/expect -f

login_file="/home/kycheng/scripts/login.txt"
echo "login_file:" $login_file

# create id_rsa
if [ ! -f ~/.ssh/id_rsa ];then
	 ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa
 else
	  echo "id_rsa has created ..."
fi

while IFS= read -r line
do
    ip=`echo $line | cut -d " " -f 1`
    user=`echo $line | cut -d " " -f 2`
    passwd=`echo $line | cut -d " " -f 3`
    expect <<EOF

    # set ssh-copy-id 
    set timeout 2
    spawn ssh-copy-id -f $user@$ip
    expect {
        "*yes/no" { send "yes\n"; exp_continue }
        "*password" { send "$passwd\n"; exp_continue }
    }

EOF
done < $login_file
