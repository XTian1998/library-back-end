from flask_restful import Resource, fields, marshal, reqparse

from App.models.book.book_model import Book
from App.utils import error_info, admin_login_required


parse = reqparse.RequestParser()
parse.add_argument("b_name", type=str, required=True, help="请填写书名")
parse.add_argument("author", type=str, required=True, help="请填写作者名")
parse.add_argument("press", type=str, required=True, help="请填写出版社名称")
parse.add_argument("price", type=float, required=True, help="请填写价格")
parse.add_argument("count", type=int, required=True, help="请填写数量")
parse.add_argument("category", type=str, required=True, help="请填写种类")
parse.add_argument("image", type=str, required=True, help="请填写图片路径")
parse.add_argument("desc", type=str, required=True, help="请填写简介")


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


class BookResource(Resource):

    def get(self, id):
        book = Book.query.filter(Book.isbn == id, Book.is_delete == False).first()
        if not book:
            return error_info(400, "书籍不存在")
        data = {
            "data": marshal(book, single_book_fields),
            "meta": {
                "status": 200,
                "msg": "获取成功"
            }
        }
        return data

    @admin_login_required
    def put(self, id):
        args = parse.parse_args()

        b_name = args.get("b_name")
        author = args.get("author")
        press = args.get("press")
        price = args.get("price")
        count = args.get("count")
        category = args.get("category")
        image = args.get("image")
        desc = args.get("desc")

        book = Book.query.filter(Book.isbn == id, Book.is_delete == False).first()
        if not book:
            return error_info(400, "书籍不存在")
        book.b_name = b_name
        book.author = author
        book.press = press
        book.price = price
        book.count = count
        book.category = category
        book.image = image
        book.desc = desc

        if not book.save():
            return error_info(400, "更改图书失败")

        data = {
            "data": marshal(book, single_book_fields),
            "meta": {
                "status": 200,
                "msg": "更改成功"
            }
        }

        return data

    @admin_login_required
    def delete(self, id):
        book = Book.query.filter(Book.isbn == id, Book.is_delete == False).first()
        if not book:
            return error_info(400, "书籍不存在")

        book.is_delete = True
        book.save()
        data = {
            "data": {
                "isbn": book.isbn
            },
            "meta": {
                "status": 204,
                "msg": "删除书籍成功"
            }
        }
        return data