#!/bin/bash
# usage: install packages locally

home_dir=$(echo ~)
proj_dir=$home_dir/widelrc
oec_dir=$proj_dir/openec-lrctradeoff

cd $oec_dir && cmake . -DFS_TYPE:STRING=HDFS3 && make
