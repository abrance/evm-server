-- 创建用户 store，密码是 123456
CREATE USER 'store'@'localhost' identified by '123456';

-- 创建数据库，存在则不创建
CREATE DATABASE IF NOT EXISTS store CHARACTER SET utf8mb4;

-- 将数据库 metadata 的所有权限都授权给用户 metadata
GRANT ALL ON store.* to 'store'@'localhost';
GRANT ALL ON store.* to 'store'@'%';

-- 允许 metadata 用户远程登录
GRANT ALL PRIVILEGES ON store.* to 'store'@'%' IDENTIFIED BY '123456' WITH GRANT OPTION;
FLUSH PRIVILEGES;