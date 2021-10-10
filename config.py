from pathlib import Path

from flask import Flask


class Config(object):
    """
    global config
    """
    DEBUG = True
    root_path = Path.cwd()


app = Flask(__name__)
# json化后中文 unicode码问题
app.config['JSON_AS_ASCII'] = False
app.config["DEBUG"] = Config.DEBUG


if __name__ == '__main__':
    print(Config.root_path)
