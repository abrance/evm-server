#!/bin/env

# 创建docker自定义网络
docker network create --subnet=192.168.2.0/24 mysubnet


docker pull mysql:5.7
docker pull redis