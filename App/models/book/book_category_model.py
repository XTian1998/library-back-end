from App.ext import db
from App.models import BaseModel


class BookCategory(BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(32), unique=True)
