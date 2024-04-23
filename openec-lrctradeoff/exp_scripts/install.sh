#!/usr/bin/expect -f

username=kycheng
passwd=kycheng

# install packages

expect <<EOF

# apt-get
set timeout -1 
spawn sudo apt-get install fio lshw
expect {
    "*password" { send "$passwd\n"; exp_continue }
    "*continue?" { send "Y\n"; exp_continue }
}

EOF
