# evm-server
easy server for vm

## PVE框架还是使用docker？
    docker在做较小的应用虚拟化时有节约资源的优势，做一个demo来说应该使用docker。
    PVE框架的优势在于本身提供了https的restful接口，如果使用PVE框架的话，这个服务可以变成了纯粹的 http 请求的转发。会显得有些无聊。
    
# TODO
    时间不足，目前数据没有使用数据库进行持久化，只能单次执行进行演示。也没有使用pytest进行测试。
    数据库设计

# 需要配置
    config.py中的 数据库信息    