from flask_restful import Resource, fields, marshal
from sqlalchemy import func

from App.models.book.book_model import Book
from App.models.book.lead_info_model import LeadInfo
from App.settings import session

single_book_fields = {
    "isbn": fields.String,
    "b_name": fields.String,
    "author": fields.String,
    "press": fields.String,
    "price": fields.Float,
    "count": fields.Integer,
    "category": fields.String,
    "image": fields.String,
    "desc": fields.String,
    "date": fields.DateTime,
    "is_delete": fields.Boolean,
}

meta_fields = {
    "status": fields.Integer,
    "msg": fields.String
}

multi_book_fields = {
    "data": fields.List(fields.Nested(single_book_fields)),
    "meta": fields.Nested(meta_fields)
}


class PopularBookResource(Resource):
    def get(self):
        list = session.query(LeadInfo.isbn, func.count(LeadInfo.oid)).group_by(LeadInfo.isbn).order_by(-func.count(LeadInfo.oid)).all()
        popular_list = []
        num = 0
        for book in list:
            if num >= 5:
                continue
            book_info = Book.query.filter(Book.isbn == book[0]).first()
            popular_list.append(book_info)
            num = num + 1
        data = {
            "data": popular_list,
            "meta": {
                "status": 200,
                "msg": '获取成功'
            }
        }
        return marshal(data, multi_book_fields)