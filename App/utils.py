import uuid

from flask import request, g

from App.ext import cache
from App.models.admin.admin_user_model import AdminUser
from App.models.reader.reader_model import Reader
from App.settings import UPLOADS_DIR, FILE_PATH_PREFIX

READER_USER = "reader_user"
ADMIN_USER = "admin_user"


def error_info(status, msg):
    return {
                "data": None,
                "meta": {
                    "status": status,
                    "msg": msg
                }
            }


def generate_token(prefix):
    token = prefix + uuid.uuid4().hex
    return token


def generate_admin_user_token():
    return generate_token(prefix=ADMIN_USER)


def generate_reader_token():
    return generate_token(prefix=READER_USER)


def get_admin_user(user_id):

    if not user_id:
        return None

    user = AdminUser.query.filter(AdminUser.id == user_id).first()
    if user:
        return user
    return None


def get_reader(user_id):

    if not user_id:
        return None

    user = Reader.query.filter(Reader.id == user_id).first()
    if user:
        return user
    return None


def admin_login_required(fun):

    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return error_info(401, "请先登录")

        if not token.startswith(ADMIN_USER):
            return error_info(401, "没有权限")

        user_id = cache.get(token)

        if not user_id:
            return error_info(401, "用户不存在")

        user = get_admin_user(user_id)

        if not user:
            return error_info(401, "用户不存在")

        g.user = user
        g.auth = token
        return fun(*args, **kwargs)
    return wrapper


def reader_login_required(fun):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return error_info(401, "请先登录")

        if not token.startswith(READER_USER):
            return error_info(401, "没有权限")

        user_id = cache.get(token)

        if not user_id:
            return error_info(401, "用户不存在")

        user = get_reader(user_id)

        if not user:
            return error_info(401, "用户不存在")

        g.user = user
        g.auth = token
        return fun(*args, **kwargs)
    return wrapper


def filename_transfer(filename):
    ext_name = filename.rsplit(".")[1]

    new_filename = uuid.uuid4().hex + '.' + ext_name

    save_path = UPLOADS_DIR + "/" +new_filename

    upload_path = FILE_PATH_PREFIX + "/" + new_filename

    return save_path, upload_path