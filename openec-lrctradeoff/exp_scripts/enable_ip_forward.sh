#!/bin/bash
# usage: init ipv4 forward

passwd=kycheng

echo $passwd | sudo -S sysctl -w net.ipv4.ip_forward=1