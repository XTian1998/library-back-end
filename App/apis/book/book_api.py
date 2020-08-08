import datetime
import math

from flask_restful import Resource, reqparse, fields, marshal

from App.models.book.book_model import Book
from App.utils import admin_login_required, error_info

parse = reqparse.RequestParser()
parse.add_argument("isbn", type=str, required=True, help="请填写isbn号")
parse.add_argument("b_name", type=str, required=True, help="请填写书名")
parse.add_argument("author", type=str, required=True, help="请填写作者名")
parse.add_argument("press", type=str, required=True, help="请填写出版社名称")
parse.add_argument("price", type=float, required=True, help="请填写价格")
parse.add_argument("count", type=int, required=True, help="请填写数量")
parse.add_argument("category", type=str, required=True, help="请填写种类")
parse.add_argument("image", type=str, required=True, help="请填写图片路径")
parse.add_argument("desc", type=str, required=True, help="请填写简介")

parse_query = reqparse.RequestParser()
parse_query.add_argument("query", type=str, required=True, help="请提供query参数")
parse_query.add_argument("pagenum", type=int, required=True, help="请提供pagenum参数")
parse_query.add_argument("pagesize", type=int, required=True, help="请提供pagesize参数")

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


multi_book_fields = {
    "total": fields.Integer,
    "pagenum": fields.Integer,
    "pagesize": fields.Integer,
    "books": fields.List(fields.Nested(single_book_fields)),
}


class BooksResource(Resource):
    def get(self):
        args= parse_query.parse_args()
        query = args.get("query")
        pagenum = args.get("pagenum")
        pagesize = args.get("pagesize")

        if query == "":
            books_return = Book.query.filter(Book.is_delete == False).offset(pagesize* (pagenum-1)).limit(pagesize)
            data_content = {
                "total": Book.query.filter(Book.is_delete == False).count(),
                "pagenum": pagenum,
                "pagesize": pagesize,
                "books": books_return,
            }
        else:
            books = Book.query.filter(Book.b_name.like("%"+query+"%"), Book.is_delete == False)
            books_return = books.offset(pagesize* (pagenum-1)).limit(pagesize)
            data_content = {
                "total": books.count(),
                "pagenum": pagenum,
                "books": books_return,
            }
        data = {
            "data": marshal(data_content, multi_book_fields),
            "meta": {
                "status": 200,
                "msg": "获取成功"
            }
        }
        return data

    @admin_login_required
    def post(self):
        args = parse.parse_args()
        isbn = args.get("isbn")
        b_name = args.get("b_name")
        author = args.get("author")
        press = args.get("press")
        price = args.get("price")
        count = args.get("count")
        category = args.get("category")
        image = args.get("image")
        desc = args.get("desc")

        if Book.query.filter(Book.isbn == isbn, Book.is_delete == True).first():
            book = Book.query.filter(Book.isbn == isbn, Book.is_delete == True).first()
            book.is_delete = False
            book.save()

        else:
            book = Book()
            book.isbn = isbn
            book.b_name = b_name
            book.author = author
            book.press = press
            book.price = price
            book.count = count
            book.category = category
            book.image = image
            book.desc = desc
            book.date = datetime.datetime.now()

            if not book.save():
                return error_info(400, "添加图书失败")

        data = {
            "data": marshal(book, single_book_fields),
            "meta": {
                "status": 201,
                "msg": "添加成功"
            }
        }

        return data



