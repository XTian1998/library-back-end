from App.ext import db
from App.models import BaseModel
from App.models.book.book_model import Book
from App.models.reader.reader_model import Reader


class BookComment(BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rid = db.Column(db.String(16), db.ForeignKey(Reader.id))
    isbn = db.Column(db.String(32), db.ForeignKey(Book.isbn))
    date = db.Column(db.DateTime)
    content = db.Column(db.String(512))