import os
import sys

from app.apis import app
from config import Config

apps_path = './app'
sys.path.append(os.path.abspath(apps_path))


def run():
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=8888)


if __name__ == '__main__':
    run()
