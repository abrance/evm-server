import contextlib
import os
import sys
from datetime import datetime
import base64

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

import config
from app.log import logger
from app.utils import dock

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base


class CommitException(BaseException):
    pass


class DuplicationException(BaseException):
    pass


class DuplicateKeyException(BaseException):
    pass


Base = declarative_base()


# 用户信息表
class User(Base):
    __tablename__ = 'user'
    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = sqlalchemy.Column(sqlalchemy.String(32), nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String(32), nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.String(11), nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String(32), nullable=False)
    is_delete = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False)
    create_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.now())


class ResourcePool(Base):
    __tablename__ = 'resource_pool'
    rp_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    # ip = sqlalchemy.Column(sqlalchemy.String(15), nullable=False)
    port = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    # 未分配为0 mysql为1 redis为2
    pool_type = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    # 0为未使用
    resource_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    resource_username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    resource_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    #     resource_name VARCHAR(32) ,                         -- 资源名
    #     resource_username VARCHAR(32) ,                     -- 资源的用户名
    #     resource_password VARCHAR(255) ,                    -- 资源的密码
    is_used = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False, default=0)
    create_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.now())


class Database(object):
    """处理资源申请"""

    def __new__(cls):
        """
        简单的单例
        """
        if __name__ != '__main__':
            _, module_name = os.path.split(sys.argv[0])
            file_name = module_name.split('.')[0]  # 后缀是py或pyc，后缀为exe时，运行可能不带exe
            module = sys.modules.get(__name__[-len(file_name):])  # 一定是同一个文件，因为实例化时进到这里
            if module:
                cls = getattr(module, cls.__name__)
        if cls.instance is None:
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.engine = sqlalchemy.create_engine(
            config.Config.db_conn_str,
            echo=True,  # 输出详细的数据库 SQL 语句
            pool_recycle=3600  # 要求取得的连接不超过一个小时
            # 详情请看官方文档的说明
            # http://docs.sqlalchemy.org/en/rel_1_1/core/pooling.html#setting-pool-recycle
        )
        self.Session = sessionmaker(bind=self.engine)

    # 下面函数管理 session 的生命周期，原因详情请看下面给出的官方文档
    # http://docs.sqlalchemy.org/en/rel_1_1/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
    @contextlib.contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error("exception occurs: {}, {}".format(type(e), e))
            if isinstance(e, IntegrityError):
                ecode = e.orig.args[0]
                if ecode == 1062:  # Duplicate key
                    raise DuplicateKeyException
                else:
                    session.rollback()
                    logger.error("> session commit failed 1, rollback")
                    raise CommitException
            else:
                session.rollback()
                logger.error("> session commit failed 2, rollback")
                raise CommitException
        finally:
            session.close()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def destroy_session(self):
        self.engine.dispose()

    def create_mysql(self, user_id, dbname, db_username, db_password, db_charset):
        """
        创建一个mysql实例。需要指定
        ip, port, dbname, db-username, db-password, db-charset
        为了不造成资源冲突问题，使用队列实现申请资源
        :return:
        """
        try:
            with self.session_scope() as session:
                # 由系统在资源池中分配ip port等资源
                min_port = session.query(func.min(ResourcePool.port)).filter(
                    ResourcePool.is_used == 0
                )
                if min_port and min_port > 1023:
                    # 不能占用保留端口号
                    port = min_port
                    ret = dock.new_mysql(user_id, dbname, port, db_username, db_password, db_charset)
                    if ret:
                        rp_row = ResourcePool(
                            port=port,
                            pool_type=1,
                            user_id=user_id,
                            is_used=True,
                            resource_name=dbname,
                            resource_username=db_username,
                            # 密码至少不明文存储
                            resource_password=base64.b64encode(db_password),
                            create_time=datetime.now()
                        )
                        session.add(rp_row)
                    else:
                        return False
                else:
                    logger.error('min_port error, check db')
                    return False
        except Exception as e:
            logger.error(e)
            return False

    def create_redis(self, user_id, dbname, db_password, db_max_memory):
        try:
            with self.session_scope() as session:
                min_port = session.query(func.min(ResourcePool.port)).filter(
                    ResourcePool.is_used == 0
                )
                if min_port and min_port > 1023:
                    # 不能占用保留端口号
                    port = min_port
                    ret = dock.new_redis(user_id, dbname, port, db_password, db_max_memory)
                    if ret:
                        rp_row = ResourcePool(
                            port=port,
                            pool_type=2,
                            user_id=user_id,
                            is_used=True,
                            resource_password=base64.b64encode(db_password),
                            resource_name=dbname,
                            create_time=datetime.now()
                        )
                        session.add(rp_row)
                    else:
                        logger.error('docker create redis fail')
                        return False
                else:
                    logger.error('min_port error, check db')
                    return False
        except Exception as e:
            logger.error(e)
            return False

    def resource_ls(self, user_id):
        try:
            with self.session_scope() as session:
                query_rp = session.query(ResourcePool).filter(
                    ResourcePool.is_used == 1, ResourcePool.user_id == user_id
                )
                row_rp = query_rp.first()
                ls = []
                if row_rp:
                    for row_rp in query_rp.all():
                        if row_rp.pool_type == 1:
                            pool_type = 'mysql'
                        elif row_rp.pool_type == 2:
                            pool_type = 'redis'
                        elif row_rp.pool_type == 0:
                            pool_type = 'empty'
                        else:
                            pool_type = 'unknown'
                        ls.append({
                            'rp_id': row_rp.rp_id,
                            'pool_type': pool_type,
                            'url': '{}:{}'.format(config.Config.host, row_rp.port),
                            'resource_name': row_rp.resource_name,
                            'resource_username': row_rp.resource_username,
                            'resource_password': row_rp.resource_password,
                            'is_used': row_rp.is_used,
                            'create_time': row_rp.create_time
                        })
                return ls
        except Exception as e:
            logger.error(e)
            return False

    def resource_conf(self, user_id, rp_id):
        try:
            with self.session_scope() as session:
                resource = session.query(ResourcePool).filter(
                    ResourcePool.rp_id == rp_id, ResourcePool.user_id == user_id
                )
                rp_row = resource.first()
                file = ''
                if rp_row:
                    if rp_row.pool_type == 1:
                        file = '/data/mycnf/{}-{}/my.cnf'.format(user_id, rp_row.resource_name)
                    elif rp_row.pool_type == 2:
                        file = '/data/redis/{}-{}/redis.conf'.format(user_id, rp_row.resource_name)
                    else:
                        pass
                    return file
                else:
                    logger.error('rp_id no found')
                    return False
        except Exception as e:
            logger.error(e)
            return False

    def resource_manage(self, user_id, rp_id, cmd):
        try:
            with self.session_scope() as session:
                resource = session.query(ResourcePool).filter(
                    ResourcePool.rp_id == rp_id, ResourcePool.user_id == user_id
                )
                rp_row = resource.first()
                if rp_row:
                    ret = dock.manage(rp_row.resource_name, cmd)
                    return ret
                else:
                    logger.error('{} no existed'.format(rp_id))
                    return False
        except Exception as e:
            logger.error(e)
            return False


db = Database()
