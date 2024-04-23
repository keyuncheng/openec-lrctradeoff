#!/usr/bin/bash

if [ "$#" != "1" ]; then
    echo "Usage: $0 file/dir" >&2
    exit 1
fi

file=$1

login_file="/home/kycheng/scripts/login.txt"
echo "login_file:" $login_file

while IFS= read -r line
do
    ip=`echo $line | cut -d " " -f 1`
    user=`echo $line | cut -d " " -f 2`
    passwd=`echo $line | cut -d " " -f 3`
    
    rsync -av $file $user@$ip:$file
done < $login_file
