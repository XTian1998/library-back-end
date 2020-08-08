import datetime

from flask_restful import Resource, fields, marshal, reqparse

from App.ext import db
from App.models.book.lead_info_model import LeadInfo
from App.models.reader.reader_model import Reader
from App.settings import session
from App.utils import admin_login_required, error_info

parse = reqparse.RequestParser()
parse.add_argument("query", type=str, required=True, help="请输入参数")

single_overtime_lead_info_fields = {
    "oid": fields.String,
    "isbn": fields.String,
    "lend_date": fields.DateTime,
    "status": fields.Integer
}

black_user_fields = {
    "id": fields.String,
    "username": fields.String,
    "status": fields.Boolean
}

black_user_data_fields = {
    "id": fields.String,
    "name": fields.String,
    "status": fields.Boolean,
    "overtime_lead_info": fields.List(fields.Nested(single_overtime_lead_info_fields))
}

meta_fields = {
    "status": fields.Integer,
    "msg": fields.String
}
black_list_fields = {
    "data": fields.List(fields.Nested(black_user_data_fields)),
    "meta": fields.Nested(meta_fields)
}


class BlackListResource(Resource):

    def get(self):
        args = parse.parse_args()
        query = args.get("query")
        db.session.commit()
        if query == "":
            black_list = session.query(Reader.id, Reader.name, Reader.status).filter(Reader.status == True).all()
        else:
            black_list = session.query(Reader.id, Reader.name, Reader.status).filter(Reader.status == True, Reader.id == query).all()
            if not black_list:
                return error_info(400, "该用户不存在或未违规")
        black_list_return = []
        for black_user in black_list:
            overtime_lead_info = LeadInfo.query.filter(LeadInfo.status == 2, LeadInfo.rid == black_user[0]).all()
            black_user_data = {
                "id": black_user[0],
                "name": black_user[1],
                "status": black_user[2],
                "overtime_lead_info": overtime_lead_info
            }
            black_list_return.append(black_user_data)
        data = {
            "data": black_list_return,
            "meta": {
                "status": 200,
                "msg": "获取成功"
            }
        }
        return marshal(data, black_list_fields)

    @admin_login_required
    def put(self):
        db.session.commit()
        overtime_lead_info_list = LeadInfo.query.filter(LeadInfo.status == 0, LeadInfo.lend_date < datetime.datetime.now() - datetime.timedelta(days=60)).all()
        for overtime_lead_info in overtime_lead_info_list:
            overtime_lead_info.status = 2
            overtime_lead_info.save()

            rid = overtime_lead_info.rid
            reader = Reader.query.filter(Reader.id == rid).first()
            if not reader.status:
                reader.status = True
                reader.save()
        data = {
            "data": None,
            "meta": {
                "status": 200,
                "msg": "更新黑名单成功"
            }
        }
        return data


class BlackUserResource(Resource):

    def put(self, id):
        black_user = Reader.query.filter(Reader.status == True, Reader.id == id).first()
        if not black_user:
            return error_info(400, "该用户不存在或未违规")

        overtime_lead_info = LeadInfo.query.filter(LeadInfo.status == 2, LeadInfo.rid == id).first()
        if overtime_lead_info:
            return error_info(400, "该用户仍有违规记录")

        black_user.status = False
        black_user.save()
        data = {
            "data": marshal(black_user, black_user_fields),
            "meta": {
                "status": 200,
                "msg": "账号恢复成功"
            }
        }
        return data