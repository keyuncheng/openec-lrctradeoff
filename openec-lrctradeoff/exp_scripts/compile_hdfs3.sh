#!/bin/bash
# usage: install packages locally
# NOTE: please ensure all packages are downloaded accordingly

username=kycheng
passwd=kycheng

home_dir=$(echo ~)
pkg_dir=$home_dir/packages
proj_dir=$home_dir/widelrc
oec_dir=$proj_dir/openec-lrctradeoff

if [ -d $pkg_dir ];then
    echo "package directory $pkg_dir exist, continue"
else
    echo "error: package directory $pkg_dir not exit, abort"
    exit 0
fi

cd $home_dir
git clone https://github.com/keyuncheng/widelrc/archive/refs/heads/master.zip -O widelrc.zip
unzip widelrc.zip
mv widelrc-master widelrc
cd $oec_dir/hdfs3.3.4-integration
sed -i "s%^HADOOP\_SRC\_DIR.*%HADOOP\_SRC\_DIR=${pkg_dir}\/hadoop-3.3.4-src%g" install.sh
bash install.sh
cp -r $pkg_dir/hadoop-3.3.4-src/hadoop-dist/target/hadoop-3.3.4 $home_dir
cp -r $pkg_dir/hadoop-3.3.4-src/oeclib $home_dir/hadoop-3.3.4

