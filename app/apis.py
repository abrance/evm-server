import json

from app.log import logger
from app.resource import db
from app.utils import verify_password, generate_auth_token, res, error, login_required
from config import app

from flask import jsonify, request


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
        print("token {}".format(token))
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
    dbname, db_username, db_password, db_max_memory = \
        info.get('dbname'), info.get('db_username'), info.get('password'), info.get('db_max_memory')
    pass
