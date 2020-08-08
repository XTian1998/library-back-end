from flask_restful import Resource, reqparse, marshal, fields

from App.models.book.book_model import Book
from App.models.book.lead_info_model import LeadInfo
from App.models.reader.reader_model import Reader
from App.settings import session
from App.utils import error_info

parse = reqparse.RequestParser()
parse.add_argument("type", type=str, required=True, help="请提供操作参数")

lead_info_fields = {
    "oid": fields.String,
    "rid": fields.String,
    "isbn": fields.String,
    'b_name': fields.String,
    "lend_date": fields.DateTime,
    "back_date": fields.DateTime,
    "status": fields.Integer,
    "b_name": fields.String
}

meta_fields = {
    "status": fields.Integer,
    "msg": fields.String
}

lead_info_list_fields = {
    "data": fields.List(fields.Nested(lead_info_fields)),
    "meta": fields.Nested(meta_fields)
}

lead_history_fields = {
    "rid": fields.String,
    "name": fields.String,
    "phone": fields.String,
    "lead_history": fields.List(fields.Nested(lead_info_fields))
}


class PersonalLeadInfo(Resource):

    def get(self, id):
        args = parse.parse_args()
        type = args.get("type")

        if type == "history":
            reader = Reader.query.filter(Reader.id == id).first()
            if not reader:
                return error_info(400, "该用户不存在")
            lead_info_list = LeadInfo.query.filter(LeadInfo.status == 1, LeadInfo.rid == id).all()
            for lead_info in lead_info_list:
                book = Book.query.filter(Book.isbn == lead_info.isbn).first()
                lead_info.b_name= book.b_name
            data_content = {
                "rid": reader.id,
                "name": reader.name,
                "phone": reader.phone,
                "lead_history": lead_info_list
            }
            data = {
                "data": marshal(data_content, lead_history_fields),
                "meta": {
                    "status": 200,
                    "msg": "获取成功"
                }
            }
            return data

        elif type == "leading":
            reader = Reader.query.filter(Reader.id == id).first()
            if not reader:
                return error_info(400, "该用户不存在")
            lead_info_list = session.query(LeadInfo).filter(LeadInfo.status != 1, LeadInfo.rid == id).all()
            for lead_info in lead_info_list:
                book = Book.query.filter(Book.isbn == lead_info.isbn).first()
                lead_info.b_name= book.b_name
            data = {
                "data": lead_info_list,
                "meta": {
                    "status": 200,
                    "msg": "获取成功"
                }
            }
            return marshal(data, lead_info_list_fields)
        else:
            return error_info(400, "请提供正确的参数")
