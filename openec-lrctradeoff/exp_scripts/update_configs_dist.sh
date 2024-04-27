#!/bin/bash

source "./config.sh"

home_dir=$(echo ~)
proj_dir=${home_dir}/widelrc/openec-lrctradeoff
config_dir=${proj_dir}/conf
config_filename=sysSetting.xml
hdfs_config_dir=${proj_dir}/hdfs3.3.4-integration/conf
hadoop_home_dir=$(echo $HADOOP_HOME)


# update configs
bash copy_dist.sh ${config_dir}/${config_filename} ${config_dir}
cp -r ${hdfs_config_dir}/* ${hadoop_home_dir}/etc/hadoop
chmod 777 ${hadoop_home_dir}/etc/hadoop/rack_topology.sh
bash copy_dist.sh ${hadoop_home_dir}/etc/hadoop ${hadoop_home_dir}/etc
bash run_script_dist.sh update_ip.sh
