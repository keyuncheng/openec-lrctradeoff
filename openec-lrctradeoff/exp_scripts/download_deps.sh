#!/bin/bash
# usage: download packages locally

username=kycheng
passwd=kycheng

home_dir=/home/$username
pkg_dir=$home_dir/packages

mkdir -p $pkg_dir
cd $pkg_dir

# dependencies (redis v3.2.8)
wget https://download.redis.io/releases/redis-3.2.8.tar.gz

# dependencies (hiredis v0.13.3)
wget https://github.com/redis/hiredis/archive/refs/tags/v0.13.3.tar.gz -O hiredis-0.13.3.tar.gz

# dependencies (gf-complete Ceph's mirror)
wget https://github.com/ceph/gf-complete/archive/refs/heads/master.zip -O gf-complete.zip

# dependencies (ISA-L v2.14.0)
wget https://github.com/intel/isa-l/archive/refs/tags/v2.30.0.tar.gz -O isa-l-2.30.0.tar.gz

# dependencies (Hadoop 3.3.4)
wget https://archive.apache.org/dist/hadoop/common/hadoop-3.3.4/hadoop-3.3.4-src.tar.gz
