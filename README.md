# evm-server
    easy server for vm
    简单的flask服务：通过docker创建mysql或redis资源，并进行管理。

## PVE框架还是使用docker？
    docker在做较小的应用虚拟化时有节约资源的优势，做一个demo来说应该使用docker。
    PVE框架的优势在于本身提供了https的restful接口，如果使用PVE框架的话，这个服务可以变成了纯粹的 http 请求的转发。会显得有些无聊。
    
# TODO
    时间不足，没有画出全部的流程图。
    没有进行pytest进行测试

# 需要配置
    config.py中的 数据库信息   
 
# 笔试要求
### 服务以 HTTP REST API 的方式提供接口，部分示例发送接口
    app/apis flask rest接口实现

### 申请一个新的 MySQL/Redis 资源实例
    由 create_mysql create_redis 接口为入口，交给db组件进行集中处理，如果dock模块执行成功就更新数据表。

### 查看某个实例的配置信息
    resource_conf 接口将配置文件取出

### MySQL、Redis 服务可以在服务端用 Docker 容器启动，也可以使用其他方式
    resource_manage 接口实现docker进行资源管理
### 分配出的不同实例之间需要避免端口等资源冲突
    自己导入资源数据到resource_pool 表中，使用数据库进行资源管理，防止资源冲突（总是使用还没有被使用的资源）
### 资源的连接、鉴权等信息应该随机生成，部分必须的信息：MySQL 连接地址、数据库名称、用户号、密码 Redis 连接地址、密码
    资源的创建时，用户都可以自定义连接地址，资源名称，用户名，用户密码等信息。如果用户不设置密码，就随机16位字符串作为密码，密码可查看(通过base64encode)。
    
### 完整的项目架构图、项目安装、使用以及 README 文档
    架构图 asciiflow.txt
    安装脚本在scripts文件夹中
    main.py 为程序入口
    
### MySQL 与 Redis 实例支持不同的个性化配置，比如：Redis 可以由用户设置数据最大占用空间，MySQL 可以由用户设置数据库字符集
    已通过创建实例时的接口进行实现可配置这两项
   
# PS
    自定义了token登陆鉴权机制
    
# github地址
    https://github.com/abrance/evm-server/