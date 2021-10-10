import time
from functools import wraps

from app.log import logger

from flask import jsonify, request
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature


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
        cost_time = end_time-start_time
        logger.debug("{}消耗时间为{}".format(func.__name__, cost_time))
        return ret
    return wrapper
