import datetime
import math

from flask_restful import Resource, reqparse, fields, marshal

from App.models.book.book_info_model import BookInfo
from App.models.book.book_model import Book
from App.models.book.lead_info_model import LeadInfo
from App.models.reader.reader_model import Reader
from App.utils import error_info, admin_login_required

parse = reqparse.RequestParser()
parse.add_argument("rid", type=str, required=True, help="请输入学号")
parse.add_argument("isbn", type=str, required=True, help="请输入ISBN号")

parse_query = reqparse.RequestParser()
parse_query.add_argument("pagenum", type=int, required=True, help="请输入页数")
parse_query.add_argument("pagesize", type=int, required=True, help="请输入页面大小")

lead_info_fields = {
    "oid": fields.String,
    "rid": fields.String,
    "isbn": fields.String,
    "lend_date": fields.DateTime,
    "back_date": fields.DateTime,
    "status": fields.Integer,
    "b_name": fields.String
}

lead_info_list_fields = {
    "total": fields.Integer,
    "pagenum": fields.Integer,
    "pagesize": fields.Integer,
    "list": fields.List(fields.Nested(lead_info_fields))
}


class LeadInfoResource(Resource):

    @admin_login_required
    def get(self):
        args = parse_query.parse_args()
        pagenum = args.get("pagenum")
        pagesize = args.get("pagesize")

        lead_info_list = LeadInfo.query.filter(LeadInfo.status != 1)
        lead_info_list_return = lead_info_list.offset(pagesize* (pagenum-1)).limit(pagesize).all()
        for lead_info in lead_info_list_return:
            book = Book.query.filter(Book.isbn == lead_info.isbn).first()
            lead_info.b_name = book.b_name
        data_content = {
            "total": lead_info_list.count(),
            "pagenum": pagenum,
            "pagesize": pagesize,
            "list": lead_info_list_return,
        }
        data = {
            "data": marshal(data_content, lead_info_list_fields),
            "meta": {
                "status": 200,
                "msg": "获取成功"
            }
        }
        return data

    @admin_login_required
    def post(self):
        args= parse.parse_args()
        rid = args.get("rid")
        isbn = args.get("isbn")

        lead_info = LeadInfo()
        lead_info.rid = rid
        lead_info.isbn = isbn
        lead_info.oid = rid + isbn + datetime.datetime.now().strftime("%Y%m%d")
        lead_info.lend_date = datetime.datetime.now().date()

        reader = Reader.query.filter(Reader.id == rid).first()
        if not reader:
            return error_info(400, "读者不存在")

        if reader.status:
            return error_info(400, "该账号已被冻结")

        book = Book.query.filter(Book.isbn == isbn).first()
        if not book:
            return error_info(400, "该书籍不存在")

        book_info = BookInfo.query.filter(BookInfo.rid == rid, BookInfo.isbn == isbn).first()
        if not book_info:
            return error_info(400, "未预约该书籍")

        if not lead_info.save():
            return error_info(400, "操作失败")

        book_info.delete()

        data = {
               "data": marshal(lead_info, lead_info_fields),
               "meta": {
                    "status": 201,
                    "msg": "借阅书籍成功"
                }
        }

        return data

    @admin_login_required
    def put(self):
        args= parse.parse_args()
        rid = args.get("rid")
        isbn = args.get("isbn")

        reader = Reader.query.filter(Reader.id == rid).first()
        if not reader:
            return error_info(400, "读者不存在")

        book = Book.query.filter(Book.isbn == isbn).first()
        if not book:
            return error_info(400, "该书籍不存在")

        lead_info = LeadInfo.query.filter(LeadInfo.rid == rid, LeadInfo.isbn == isbn, LeadInfo.status != 1).first()
        if not lead_info:
            return error_info(400, "未借阅该书籍")

        lead_info.back_date = datetime.datetime.now().date()
        lead_info.status = 1
        if not lead_info.save():
            return error_info(400, "操作失败")

        book.count = book.count + 1
        book.save()

        data = {
               "data": marshal(lead_info, lead_info_fields),
               "meta": {
                    "status": 200,
                    "msg": "归还书籍成功"
                }
        }

        return data
