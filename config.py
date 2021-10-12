from pathlib import Path

from flask import Flask


class Config(object):
    """
    global config
    """
    DEBUG = True
    dbn = "mysql"
    mysql_engine = 'pymysql'
    user = 'store'
    password = '123456'
    host = 'localhost'
    port = '3306'
    db = 'store'
    db_conn_str = '{}+{}://{}:{}@{}:{}/{}?charset=utf8mb4'.\
        format(dbn, mysql_engine, user, password, host, port, db)
    root_path = Path.cwd()


app = Flask(__name__)
# json化后中文 unicode码问题
app.config['JSON_AS_ASCII'] = False
app.config["DEBUG"] = Config.DEBUG


if __name__ == '__main__':
    print(Config.root_path)
