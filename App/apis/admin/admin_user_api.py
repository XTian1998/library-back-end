from flask_restful import Resource, reqparse, marshal, fields
from werkzeug.security import generate_password_hash, check_password_hash

from App.ext import cache
from App.models.admin.admin_user_model import AdminUser
from App.utils import error_info, generate_admin_user_token, get_admin_user

parse_base = reqparse.RequestParser()
parse_base.add_argument("action", type=str, required=True, help="请输入请求参数")
parse_base.add_argument("id", type=str, required=True, help="请输入管理员工号")
parse_base.add_argument("password", type=str, required=True, help="请输入密码")

parse_login = parse_base.copy()

parse_register=parse_base.copy()
parse_register.add_argument("username", type=str, required=True, help="请输入用户名")


class AdminUserResource(Resource):
    def post(self):
        args = parse_base.parse_args()

        action = args.get("action")
        id = args.get("id")

        password = args.get("password")

        if action == "register":
            args_register = parse_register.parse_args()
            username = args_register.get("username")

            admin_user = AdminUser()
            admin_user.id = id
            admin_user.username = username
            admin_user.password = generate_password_hash(password)

            if not admin_user.save():
                return error_info(400, "注册失败")
            data = {
                "data": {
                    "id": admin_user.id,
                    "username": admin_user.username
                },
                "meta": {
                    "status": 201,
                    "msg": "用户创建成功"
                }
            }
            return data

        elif action == "login":
            user = get_admin_user(id)

            if not user:
                data = error_info(400, "用户不存在")
                return data
            if not check_password_hash(user.password, password):
                data = error_info(400, "密码错误")
                return data
            if user.is_delete:
                data = error_info(400, "用户不存在")
                return data

            token = generate_admin_user_token()

            cache.set(token, user.id, timeout=60*60*24*7)

            data = {
                "data": {
                    "id": user.id,
                    "username": user.username,
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
