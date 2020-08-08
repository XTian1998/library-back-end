from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash

from App.ext import cache
from App.models.reader.reader_model import Reader
from App.utils import error_info, generate_reader_token, get_reader

parse_base = reqparse.RequestParser()
parse_base.add_argument("action", type=str, required=True, help="请输入请求参数")
parse_base.add_argument("id", type=str, required=True, help="请输入学号")
parse_base.add_argument("password", type=str, required=True, help="请输入密码")

parse_login = parse_base.copy()

parse_register=parse_base.copy()
parse_register.add_argument("username", type=str, required=True, help="请输入用户名")
parse_register.add_argument("name", type=str, required=True, help="请输入姓名")
parse_register.add_argument("phone", type=str, required=True, help="请输入手机号")


class ReaderResource(Resource):

    def post(self):
        args = parse_base.parse_args()

        action = args.get("action")
        id = args.get("id")
        password = args.get("password")

        if action == "register":
            args_register = parse_register.parse_args()
            username = args_register.get("username")
            name = args_register.get("name")
            phone = args_register.get("phone")
            if Reader.query.filter(Reader.id == id).first():
                return error_info(400, "该用户已注册")
            if Reader.query.filter(Reader.username == username).first():
                return error_info(400, "该用户名已存在")

            reader = Reader()
            reader.id = id
            reader.username = username
            reader.password = generate_password_hash(password)
            reader.phone = phone
            reader.name = name

            if not reader.save():
                return error_info(400, "注册失败")
            data = {
                "data": {
                    "id": reader.id,
                    "username": reader.username,
                },
                "meta": {
                    "status": 201,
                    "msg": "注册成功"
                }
            }
            return data

        elif action == "login":
            user = get_reader(id)

            if not user:
                data = error_info(400, "用户不存在")
                return data
            if not check_password_hash(user.password, password):
                data = error_info(400, "密码错误")
                return data
            if user.is_delete:
                data = error_info(400, "用户不存在")
                return data

            token = generate_reader_token()

            cache.set(token, user.id, timeout=60*60*24*7)

            data = {
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "status": user.status,
                    "token": token
                },
                "meta": {
                    "status": 200,
                    "msg": "登录成功"
                }
            }

            return data
        else:
            data = error_info(400, "请提供正确的参数")
            return data