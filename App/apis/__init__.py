from App.apis.admin import admin_api
from App.apis.book import book_api
from App.apis.reader import reader_api


def init_api(app):
    reader_api.init_app(app)
    admin_api.init_app(app)
    book_api.init_app(app)




