# 用户信息表
create table `user`(
    user_id int auto_increment primary key NOT NULL,
    username VARCHAR(32) NOT NULL,
    email VARCHAR(32) ,
    phone CHAR(11) ,
    password CHAR(32) NOT NULL ,
    is_delete TINYINT NOT NULL ,
    create_time DATETIME NOT NULL,
    index `user_id_index` (`user_id`)
);

# 资源池信息表
create table `resource_pool`(
    rp_id int auto_increment primary key NOT NULL,
    # ip VARCHAR(15) NOT NULL ,
    port int NOT NULL ,
    pool_type TINYINT ,                                 -- 资源类型
    user_id int ,                                       -- 资源所有者id
    resource_name VARCHAR(32) ,                         -- 资源名
    resource_username VARCHAR(32) ,                     -- 资源的用户名
    resource_password VARCHAR(255) ,                    -- 资源的密码
    is_used TINYINT NOT NULL,
    create_time DATETIME NOT NULL
);
