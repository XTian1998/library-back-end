from App.ext import db
from App.models import BaseModel
from App.models.book.book_category_model import BookCategory


class Book(BaseModel):
    isbn = db.Column(db.String(32), primary_key=True)
    b_name = db.Column(db.String(64), unique=True)
    author= db.Column(db.String(32))
    press = db.Column(db.String(64))
    price = db.Column(db.Float)
    count = db.Column(db.Integer)
    category = db.Column(db.String(32), db.ForeignKey(BookCategory.category))
    image = db.Column(db.String(128))
    desc = db.Column(db.String(1024))
    date = db.Column(db.DateTime)
    is_delete = db.Column(db.Boolean, default=False)
