import datetime

from flask_restful import Resource, reqparse, fields, marshal

from App.models.book.book_comment_model import BookComment
from App.models.book.book_model import Book
from App.models.reader.reader_model import Reader
from App.utils import error_info, reader_login_required

parse = reqparse.RequestParser()
parse.add_argument("rid", type=str, required=True, help="请提供学号")
parse.add_argument("isbn", type=str, required=True, help="请提供ISBN号")
parse.add_argument("content", type=str, required=True, help="请提供评论内容")

parse_query = reqparse.RequestParser()
parse_query.add_argument("isbn", type=str, required=True, help="请提供ISBN号")

book_comment_fields = {
    "id": fields.Integer,
    "rid": fields.String,
    "isbn": fields.String,
    "date": fields.DateTime,
    "content": fields.String,
}

meta_fields = {
    "status": fields.Integer,
    "msg": fields.String
}
book_comments_fields = {
    "data": fields.List(fields.Nested(book_comment_fields)),
    "meta": fields.Nested(meta_fields)
}


class BookCommentResource(Resource):

    @reader_login_required
    def post(self):
        args = parse.parse_args()
        rid = args.get("rid")
        isbn = args.get("isbn")
        content = args.get("content")

        reader = Reader.query.filter(Reader.id == rid).first()
        if not reader:
            return error_info(400, '用户不存在')
        
        book = Book.query.filter(Book.isbn == isbn).first()
        if not book:
            return error_info(400, '该书籍不存在')

        book_comment = BookComment()
        book_comment.rid = rid
        book_comment.isbn = isbn
        book_comment.content = content
        book_comment.date = datetime.datetime.now()

        if not book_comment.save():
            return error_info(400, "超过最大评论字数")

        data = {
            "data": marshal(book_comment, book_comment_fields),
            "meta": {
                "status": 201,
                "msg": "评论成功"
            }
        }
        return data

    def get(self):
        args =parse_query.parse_args()
        isbn = args.get("isbn")

        book_comments = BookComment.query.filter(BookComment.isbn == isbn).all()

        data = {
            "data": book_comments,
            "meta": {
                "status": 200,
                "msg": "获取成功"
            }
        }

        return marshal(data, book_comments_fields)