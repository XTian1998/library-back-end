from App.ext import db
from App.models import BaseModel
from App.models.book.book_model import Book
from App.models.reader.reader_model import Reader


class BookInfo(BaseModel):
    oid = db.Column(db.String(64), primary_key=True)
    rid = db.Column(db.String(16), db.ForeignKey(Reader.id))
    isbn = db.Column(db.String(32), db.ForeignKey(Book.isbn))
    book_date = db.Column(db.DateTime)