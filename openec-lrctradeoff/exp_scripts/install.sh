#!/usr/bin/expect -f
# usage: install packages locally

username=kycheng
passwd=kycheng

home_dir=/home/$username
pkg_dir=$home_dir/packages
mkdir $pkg_dir

expect << EOF


# performance benchmark
set timeout -1 
spawn sudo apt-get -y install fio lshw iperf
expect {
    "*password" { send "$passwd\n"; exp_continue }
    "*continue?" { send "Y\n"; exp_continue }
}


# dependencies (cmake g++)
set timeout -1 
spawn sudo apt-get -y install cmake g++
expect {
    "*password" { send "$passwd\n"; exp_continue }
    "*continue?" { send "Y\n"; exp_continue }
}


# dependencies (redis v3.2.8)
wget https://download.redis.io/releases/redis-3.2.8.tar.gz -P $pkg_dir
cd $pkg_dir
tar -zxvf redis-3.2.8.tar.gz
cd redis-3.2.8
make
sudo make install
cd utils
sudo ./install server.sh
sudo service redis 6379 stop

spawn sudo sed -i 's/bind 127.0.0.0/bind 0.0.0.0/g' /etc/redis/6379.conf
expect {
    "*password" { send "$passwd\n"; exp_continue }
}

sudo service redis 6379 start


# dependencies (hiredis v1.0.0)
wget https://github.com/redis/hiredis/archive/refs/tags/v1.0.0.tar.gz -P $pkg_dir -O hiredis-1.0.0.tar.gz
cd $pkg_dir
tar zxvf hiredis-1.0.0.tar.gz
cd hiredis-1.0.0
make
sudo make install

# dependencies (gf-complete Ceph's mirror)
spawn sudo apt-get -y install libtool autoconf yasm nasm
expect {
    "*password" { send "$passwd\n"; exp_continue }
    "*continue?" { send "Y\n"; exp_continue }
}
wget https://github.com/ceph/gf-complete/archive/refs/heads/master.zip -P $pkg_dir -O gf-complete.zip
cd $pkg_dir
unzip gf-complete.zip
cd gf-complete-master/
./autogen.sh
./configure
make
sudo make install

# dependencies (ISA-L v2.14.0)
wget https://github.com/intel/isa-l/archive/refs/tags/v2.30.0.tar.gz -P $pkg_dir -O isa-l-2.30.0.tar.gz
cd $pkg_dir
tar zxvf isa-l-2.30.0.tar.gz
cd isa-l-2.30.0/
./autogen.sh
./configure
make
sudo make install


# dependencies (Java 8, Maven)
spawn sudo apt-get -y install openjdk-8-jdk maven
expect {
    "*password" { send "$passwd\n"; exp_continue }
    "*continue?" { send "Y\n"; exp_continue }
}

sed -i '/JAVA_HOME=/d' $home_dir/.bashrc
sed -i '/M2_HOME=/d' $home_dir/.bashrc
sed -i '/PATH=/d' $home_dir/.bashrc

echo -e 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' >> $home_dir/.bashrc
echo -e 'export MAVEN_HOME=/usr/share/maven' >> $home_dir/.bashrc
echo -e 'export PATH=$M2_HOME/bin:$JAVA_HOME/bin:$PATH' >> $home_dir/.bashrc


# dependencies (Hadoop 3.3.4)
wget https://downloads.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4-src.tar.gz -P $pkg_dir
cd $pkg_dir
tar zxvf hadoop-3.3.4-src.tar.gz

sed -i '/HADOOP_SRC_DIR=/d' $home_dir/.bashrc
sed -i '/HADOOP_HOME=/d' $home_dir/.bashrc
sed -i '/HADOOP_CLASSPATH=/d' $home_dir/.bashrc
sed -i '/CLASSPATH=/d' $home_dir/.bashrc
sed -i '/LD_LIBRARY_PATH=/d' $home_dir/.bashrc

echo -e 'export HADOOP_SRC_DIR=$pkg_dir/hadoop-3.3.4-src' >> $home_dir/.bashrc
echo -e 'export HADOOP_HOME=$home_dir/hadoop-3.3.4' >> $home_dir/.bashrc
echo -e 'export HADOOP_CLASSPATH=$JAVA_HOME/lib/tools.jar:$HADOOP_CLASSPATH' >> $home_dir/.bashrc
echo -e 'export CLASSPATH=$JAVA_HOME/lib:$CLASSPATH' >> $home_dir/.bashrc
echo -e 'export LD_LIBRARY_PATH=$HADOOP_HOME/lib/native:$JAVA_HOME/jre/lib/
amd64/server/:/usr/local/lib:$LD_LIBRARY_PATH' >> $home_dir/.bashrc
echo -e 'export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH' >> $home_dir/.bashrc

# install code
git clone https://github.com/keyuncheng/widelrc/archive/refs/heads/master.zip -P $home_dir -O widelrc.zip
cd $home_dir
unzip widelrc.zip
mv widelrc-master widelrc
cd widelrc/openec-lrctradeoff/hdfs3-integration
sed -i 's/HADOOP_SRC_DIR*/HADOOP_SRC_DIR=$pkg_dir/hadoop-3.3.4-src/g' install.sh
./install.sh

# compile code
proj_dir=$home_dir/widelrc
cd $proj_dir
cmake . -DFS_TYPE:STRING=HDFS3
make

###################################################################

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
