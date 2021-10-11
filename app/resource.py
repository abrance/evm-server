import os
import sys
import time
from queue import Queue

from app.log import logger


class DuplicationException(BaseException):
    pass


class ResourceHandle(object):
    """处理资源申请"""
    instance = None
    # 队列最大长度
    MAXSIZE = 1000
    # 未使用IP资源池列表
    RESOURCE_IP_POOL = ['192.168.2.{}'.format(i) for i in range(2, 255)]
    # 正在使用IP资源池列表
    DISTRIBUTED_POOL = {}

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
            cls.instance = super(ResourceHandle, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.queue = Queue(maxsize=self.MAXSIZE)

    def handle(self):
        while True:
            if self.queue.qsize() == 0:
                time.sleep(0.01)
            else:
                item = self.queue.get()
                if isinstance(item, tuple):
                    try:
                        ip, port, dbname, db_username, db_password, db_charset = item
                        if ip in self.RESOURCE_IP_POOL:
                            self.DISTRIBUTED_POOL[ip] = {
                                'ip': ip,
                                'port': port,
                                'db': [
                                    {
                                        'dbname': dbname,
                                        'db_username': db_username,
                                        'db_password': db_password,
                                        'db_charset': db_charset
                                    }
                                ]
                            }
                            self.RESOURCE_IP_POOL.remove(ip)

                            # 执行 db 初始化 TODO


                        else:
                            _item = self.DISTRIBUTED_POOL.get(ip)
                            if _item:
                                dbs = _item.get('db')
                                if dbs:
                                    for db in dbs:
                                        if db.get('dbname') == dbname:
                                            raise DuplicationException
                                    assert isinstance(dbs, list)
                                    dbs.append({
                                        'dbname': dbname,
                                        'db_username': db_username,
                                        'db_password': db_password,
                                        'db_charset': db_charset
                                    })
                                    logger.debug('dbs append {}'.format(item))
                                    # 执行连接并创建数据库 TODO


                    except DuplicationException as de:
                        logger.error('db existed: {}'.format(de))
                        return False

                    except Exception as e:
                        logger.error(e)
                        return False


def create_mysql(ip, port, dbname, db_username, db_password, db_charset):
    """
    创建一个mysql实例。需要指定
    ip, port, dbname, db-username, db-password, db-charset
    为了不造成资源冲突问题，使用队列实现申请资源
    :return:
    """

