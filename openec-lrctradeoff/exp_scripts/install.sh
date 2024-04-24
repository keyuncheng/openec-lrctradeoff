#!/usr/bin/expect -f
# usage: install packages locally

username=kycheng
passwd=kycheng


expect << EOF

# apt-get
set timeout -1 
spawn sudo apt-get -y install fio lshw
expect {
    "*password" { send "$passwd\n"; exp_continue }
    "*continue?" { send "Y\n"; exp_continue }
}

# # write string command
# set timeout -1 
# spawn bash -c "echo -n -e \"\$\" | sudo tee /etc/needrestart/conf.d/no-prompt.conf"
# expect {
#     "*password" { send "$passwd\n"; exp_continue }
# }
# 
# set timeout -1
# spawn bash -c "echo -e \"nrconf{restart} = \'a\';\" | sudo tee -a /etc/needrestart/conf.d/no-prompt.conf"
# expect {
#     "*password" { send "$passwd\n"; exp_continue }
# }

EOF
