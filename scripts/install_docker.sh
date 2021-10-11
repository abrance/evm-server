#!/bin/env

# for centos7
# docker version
# 依赖
yum install -y gcc gcc-c++
yum install -y yum-utils device-mapper-persistent-data lvm2

# 设置stable镜像仓库
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
# 更新yum软件包索引
yum makecache fast
# 安装docker-ce
yum install -y docker-ce

# 配置阿里云加速
echo '{"registry-mirrors": ["http://hub-mirror.c.163.com"] }' > /etc/docker/daemon.json

mkdir -p /data/mysql/
mkdir -p /data/mycnf/
# 启动docker
systemctl start docker

docker version
