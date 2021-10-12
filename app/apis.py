import json
import os
import random
import string

from app.log import logger
from app.resource import db
from app.utils import verify_password, generate_auth_token, res, error, login_required
from config import app

from flask import jsonify, request, send_file


@app.route('hello')
def hello():
    return jsonify(res('hello'))


@app.route('/test_post', methods=['POST'])
@login_required
def test_post():
    return jsonify(res('ok'))


@app.route("/api/login", methods=['POST'])
def login():
    info = request.data
    info = json.loads(info)
    logger.debug("info {}".format(info))
    username = info.get('username')
    pwd = info.get('password')
    logger.debug("{}\n{}".format(username, pwd))
    ret = verify_password(username, pwd)
    if ret:
        token = generate_auth_token(username)
        logger.debug("token {}".format(token))
        return jsonify(res(token))
    else:
        return jsonify(error("auth error"))


# - 申请一个新的 MySQL 资源实例
@app.route('/resource/create_mysql', methods=['POST'])
@login_required
def create_mysql():
    info = request.form
    user_id = info.get('user_id')
    dbname, db_username, db_password, db_charset = \
        info.get('dbname'), info.get('db_username'), info.get('password'), info.get('db_charset')
    if not db_password:
        # 如果用户不设置密码，就随机16位字符串
        db_password = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    ret = db.create_mysql(user_id, dbname, db_username, db_password, db_charset)
    if ret:
        return jsonify(res('ok'))
    else:
        return jsonify(error('create mysql fail'))


# - 申请一个新的 Redis 资源实例
@app.route('/resource/create_redis', methods=['POST'])
@login_required
def create_redis():
    info = request.form
    user_id = info.get('user_id')
    dbname, db_password, db_max_memory = \
        info.get('dbname'), info.get('password'), info.get('db_max_memory')
    ret = db.create_redis(user_id, dbname, db_password, db_max_memory)
    if ret:
        return jsonify(res('ok'))
    else:
        return jsonify(error('create redis fail'))


# 查看用户所拥有的资源
@app.route('/resource/ls', methods=['POST'])
@login_required
def resource_ls():
    info = request.form
    user_id = info.get('user_id')
    ret_ls = db.resource_ls(user_id)
    if ret_ls is False:
        return jsonify(error('resource source fail'))
    else:
        return jsonify(res(ret_ls))


# 查看资源配置
@app.route('/resource/conf', methods=['POST'])
@login_required
def resource_conf():
    info = request.form
    user_id, rp_id = info.get('user_id'), info.get('rp_id')
    ret = db.resource_conf(user_id, rp_id)
    if ret:
        conf = ret
        return send_file(conf)


# 资源管理，启动重启停止
@app.route('/resource/manage', methods=['POST'])
@login_required
def resource_manage():
    info = request.form
    user_id, rp_id = info.get('user_id'), info.get('rp_id')
    cmd = info.get('command')
    if cmd in ['start', 'restart', 'stop']:
        pass
    else:
        return jsonify(error('resource manage fail'))

    ret = db.resource_manage(user_id, rp_id, cmd)
    if ret:
        return jsonify(res('ok'))
    else:
        return jsonify(error('resource manage fail'))
