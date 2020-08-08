from flask import Flask
from flask_cors import CORS

from App.apis import init_api
from App.ext import init_ext
from App.settings import Config


def create_app():
    app = Flask(__name__)

    # 初始化项目配置
    app.config.from_object(Config)

    # 初始化扩展库
    init_ext(app)

    # 初始化路由
    init_api(app=app)

    CORS(app, supports_credentials=True)

    return app
