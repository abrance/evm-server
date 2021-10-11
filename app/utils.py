import subprocess
import time
from functools import wraps

from app.log import logger

from flask import jsonify, request
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature


# from docker import Client


def generate_auth_token(user_id, expiration=36000):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({
        'user': user_id
    }).decode()


def verify_auth_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
        return data
    except SignatureExpired as se:
        logger.error(se)
        return None
    except BadSignature as be:
        logger.error(be)
        return None


def error(msg, code=400):
    return {'code': code, 'res': '', 'msg': msg}


def res(data):
    return {'code': 200, 'res': data}


def verify_password(user, password):
    if user:
        # db中进行验证
        if user == 'admin@wz.com' and password == "123456":
            print('pass')
            return True
    return False


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", default=None)
        if token:
            data = verify_auth_token(token)
            logger.debug('token: {}'.format(data))
            if data:
                return f(*args, **kwargs)
        else:
            return jsonify(error("403"))

    return wrapper


def timing_(func):
    # 2020/4/10 计时装饰器
    def wrapper(*args, **kwargs):
        start_time = time.time()
        ret = func(*args, **kwargs)
        end_time = time.time()
        cost_time = end_time - start_time
        logger.debug("{}消耗时间为{}".format(func.__name__, cost_time))
        return ret

    return wrapper


def subprocess_popen(statement):
    """
    执行shell命令，并返回结果
    :param statement:
    :return:
    """
    p = subprocess.Popen(statement, shell=True, stdout=subprocess.PIPE)  # 执行shell语句并定义输出格式
    while p.poll() is None:
        # 判断进程是否结束（Popen.poll()用于检查子进程（命令）是否已经执行结束，没结束返回None，结束后返回状态码）
        if p.wait() is not 0:
            # 判断是否执行成功（Popen.wait()等待子进程结束，并返回状态码；如果设置并且在timeout指定的秒数之后进程还没有结束，将会抛出一个TimeoutExpired异常。）
            logger.error("命令执行失败，请检查设备连接状态")
            return False
        else:
            re = p.stdout.readlines()  # 获取原始执行结果
            result = []
            for i in range(len(re)):  # 由于原始结果需要转换编码，所以循环转为utf8编码并且去除\n换行
                _res = re[i].decode('utf-8').strip('\r\n')
                result.append(_res)
            return result


class DockerAPI(object):
    """
    TODO docker-py 是个好东西，但是文档比较难啃。以后可以改为用docker-py api

    """
    MYSQL_ROOT_PASSWORD = 'never@guess.123'
    MY_DOCKER_SERVER = 'unix:///var/run/docker.sock'

    # 49000-49500 for mysql 49501-49900 for redis

    # def __init__(self):
    #
    #     self.client = Client(base_url='{}'.format(self.MY_DOCKER_SERVER))
    #     logger.debug(self.client.version())
    #     self.mysql_img = self.client.pull('mysql:5.7', stream=True)
    #     self.redis_img = self.client.pull('redis', stream=True)

    def new_mysql(self, name, port, db_username, db_password):
        # 这里假设name不重名，以后可以做成映射表，即name-> container-name
        # docker run -d -it -p3307:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:5.7
        result = subprocess_popen(
            'mkdir -p /data/mysql/{name} && '
            'docker run -dit -p{}:3306 --name {name} '
            '-v /data/mysql/{name}:/var/lib/mysql'
            '-v /data/mycnf/{name}/my.cnf:/etc/my.cnf'
            '-e MYSQL_ROOT_PASSWORD={pwd} mysql:5.7'.format_map({
                'name': name,
                'port': port,
                'pwd': self.MYSQL_ROOT_PASSWORD
            }
            )
        )
        if result:
            # result 为容器名
            result = subprocess_popen(
                'docker exec {} '
                'echo "CREATE USER {}@% identified by {};\nGRANT ALL ON *.* TO {}@%; > ./add_user.sql'
                'mysql -uroot -p{} -Dmysql < ./add_user.sql"'.format(
                    result, self.MYSQL_ROOT_PASSWORD, db_username, db_password, db_username)
            )
            if result:
                # 执行新增用户成功
                return True
            else:
                logger.error('container error')
                return False
        else:
            # 容器运行失败
            logger.error('container run fail')
            return False
