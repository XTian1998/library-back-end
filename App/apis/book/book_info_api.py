import datetime

from flask_restful import reqparse, Resource, fields, marshal

from App.models.book.book_info_model import BookInfo
from App.models.book.book_model import Book
from App.models.book.lead_info_model import LeadInfo
from App.models.reader.reader_model import Reader
from App.settings import session
from App.utils import error_info, reader_login_required

parse = reqparse.RequestParser()
parse.add_argument("rid", type=str, required=True, help="请输入学号")
parse.add_argument("isbn", type=str, required=True, help="请输入ISBN号")

parse_query = reqparse.RequestParser()
parse_query.add_argument("rid", type=str, required=True, help="请输入学号")

book_info_fields = {
    "oid": fields.String,
    "rid": fields.String,
    "isbn": fields.String,
    "book_date": fields.DateTime,
    "b_name": fields.String
}

book_info_list_fields = {
    "rid": fields.String,
    "name": fields.String,
    "phone": fields.String,
    "book_list": fields.List(fields.Nested(book_info_fields))
}


class BookInfoResource(Resource):

    def get(self):
        args = parse_query.parse_args()
        rid = args.get("rid")
        reader = Reader.query.filter(Reader.id == rid).first()
        if not reader:
            return error_info(400, "用户不存在")
        book_info_list = BookInfo.query.filter(BookInfo.rid == rid).all()
        for book_info in book_info_list:
            book = Book.query.filter(Book.isbn == book_info.isbn).first()
            book_info.b_name = book.b_name
        data_content = {
                "rid": rid,
                "name": reader.name,
                "phone": reader.phone,
                "book_list": book_info_list
            }
        data = {
            "data": marshal(data_content, book_info_list_fields),
            "meta": {
                "status": 200,
                "msg": "获取成功"
            }
        }
        return data

    @reader_login_required
    def post(self):
        args = parse.parse_args()
        rid = args.get("rid")
        isbn = args.get("isbn")

        book_permission = session.query(BookInfo).filter(BookInfo.rid == rid).count() + session.query(LeadInfo).filter(LeadInfo.rid == rid, LeadInfo.status != 1).count()
        if book_permission >= 3:
            return error_info(400, "已到达最大借阅数量")

        book = Book.query.filter(Book.isbn == isbn).first()
        if not book:
            return error_info(400, "该书籍不存在")
        if book.count == 0:
            return error_info(400, "该书籍暂时没有库存")

        reader = Reader.query.filter(Reader.id == rid).first()
        if not reader:
            return error_info(400, "该用户不存在")
        if reader.status:
            return error_info(400, "该账号已被冻结")

        lead_info = session.query(LeadInfo).filter(LeadInfo.rid == rid, LeadInfo.isbn == isbn, LeadInfo.status != 1).first()
        if lead_info:
            return error_info(400, "已借阅该书籍")

        book_date = datetime.datetime.now().date()
        oid = rid + isbn

        already_book = BookInfo.query.filter(BookInfo.oid == oid).first()
        if already_book:
            return error_info(400, "已预约该书籍")

        book_info = BookInfo()
        book_info.oid = oid
        book_info.rid = rid
        book_info.isbn = isbn
        book_info.book_date = book_date

        if not book_info.save():
            return error_info(400, "预约失败")

        book.count = book.count - 1
        book.save()


        data = {
            "data": marshal(book_info, book_info_fields),
            "meta": {
                "status": 201,
                "msg": "预约成功"
            }
        }
        return data

    @reader_login_required
    def delete(self):
        args = parse.parse_args()
        rid = args.get("rid")
        isbn = args.get("isbn")

        reader = Reader.query.filter(Reader.id == rid).first()
        if not reader:
            return error_info(400, "该用户不存在")

        book = Book.query.filter(Book.isbn == isbn).first()
        if not book:
            return error_info(400, "该书籍不存在")

        book_info = BookInfo.query.filter(BookInfo.rid == rid, BookInfo.isbn == isbn).first()
        if not book_info:
            return error_info(400, "未预约该书籍")

        book_info.delete()

        book.count = book.count + 1
        book.save()

        data = {
            "data": None,
            "meta": {
                "status": 204,
                "msg": "取消预约成功"
            }
        }

        return data

