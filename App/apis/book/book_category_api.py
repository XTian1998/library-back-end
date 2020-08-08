import math

from flask_restful import Resource, reqparse, marshal, fields
from sqlalchemy import func

from App.models.book.book_category_model import BookCategory
from App.models.book.book_model import Book
from App.settings import session
from App.utils import admin_login_required, error_info

parse = reqparse.RequestParser()
parse.add_argument("category", type=str, required=True, help="请提供分类名称")

parse_query = reqparse.RequestParser()
parse_query.add_argument("query", type=str, required=True, help="请提供获取类型")

parse_list = parse_query.copy()
parse_list.add_argument("category", type=str, required=True, help="请提供分类名称")
parse_list.add_argument("pagenum", type=int, required=True, help="请提供当前页数")
parse_list.add_argument("pagesize", type=int, required=True, help="请提供当前页面大小")

parse_num = parse_query.copy()

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
    "category": fields.String,
    "books": fields.List(fields.Nested(single_book_fields)),
}

num_query_fields = {
    "name": fields.String,
    "value": fields.Integer
}

category_fields = {
    "id": fields.Integer,
    "category": fields.String
}
meta_fields = {
    "status": fields.Integer,
    "msg": fields.String
}
categories_fields = {
    "data": fields.List(fields.Nested(category_fields)),
    "meta": fields.Nested(meta_fields)
}


class BookCategoryResource(Resource):

    @admin_login_required
    def post(self):
        args = parse.parse_args()
        category = args.get("category")

        if BookCategory.query.filter(BookCategory.category == category).first():
            return error_info(400, "该分类已存在")

        book_category = BookCategory()
        book_category.category = category

        if not book_category.save():
            return error_info(400, "添加分类失败")

        data = {
            "data": {
                "id": book_category.id,
                "category": book_category.category
            },
            "meta": {
                "status": 201,
                "msg": "添加分类成功"
            }
        }

        return data

    def get(self):
        args = parse_query.parse_args()
        query = args.get("query")
        if query == "list":
            args_list= parse_list.parse_args()
            category = args_list.get("category")
            pagenum = args_list.get("pagenum")
            pagesize = args_list.get("pagesize")
            books = Book.query.filter(Book.category == category, Book.is_delete == False)
            books_return = books.offset(pagesize * (pagenum - 1)).limit(pagesize)
            data_content = {
                "total": books.count(),
                "pagenum": pagenum,
                "pagesize": pagesize,
                "category": category,
                "books": books_return,
            }
            data = {
                "data": marshal(data_content, multi_book_fields),
                "meta": {
                    "status": 200,
                    "msg": "获取成功"
                }
            }
        elif query == "num":
            books = session.query(Book.category, func.count(Book.category)).group_by(Book.category).all()
            data_content = []
            for book in books:
                data = {
                    "name": book[0],
                    "value": book[1]
                }
                data_content.append(data)
            data ={
                "data": marshal(data_content, num_query_fields),
                "meta": {
                    "status": 200,
                    "msg": "获取成功"
                }
            }
        elif query == "category":
            categories = BookCategory.query.order_by(BookCategory.id).all()
            data = {
                "data": categories,
                "meta": {
                    "status": 200,
                    "msg": "获取成功"
                }
            }
            data = marshal(data, categories_fields)
        else:
            data = error_info(400, "请提供正确的参数")
        return data

