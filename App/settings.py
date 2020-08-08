import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Config:
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/Library"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = "Xtian"


engine = create_engine("mysql+pymysql://root:123456@localhost:3306/Library", max_overflow=5, isolation_level="READ UNCOMMITTED")
Session = sessionmaker(bind=engine)
session = Session()


# 图片上传的路径设置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILE_PATH_PREFIX = "/static/uploads"

UPLOADS_DIR = os.path.join(BASE_DIR, 'App/static/uploads')