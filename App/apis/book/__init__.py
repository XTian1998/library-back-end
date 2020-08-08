from flask_restful import Api

from App.apis.book.book_api import BooksResource
from App.apis.book.book_category_api import BookCategoryResource
from App.apis.book.book_comment_api import BookCommentResource
from App.apis.book.book_image_uploads_api import BookImageResource
from App.apis.book.book_info_api import BookInfoResource
from App.apis.book.book_isbn_api import BookResource
from App.apis.book.lead_info_api import LeadInfoResource
from App.apis.book.lead_info_isbn import PersonalLeadInfo
from App.apis.book.popular_book_api import PopularBookResource

book_api = Api(prefix="/book")

book_api.add_resource(BookCategoryResource, '/category/')
book_api.add_resource(BookImageResource, '/uploads/')
book_api.add_resource(BooksResource, '/')
book_api.add_resource(BookResource, '/<string:id>/')
book_api.add_resource(LeadInfoResource, '/leadinfo/')
book_api.add_resource(BookInfoResource, '/bookinfo/')
book_api.add_resource(PersonalLeadInfo, '/leadinfo/<string:id>/')
book_api.add_resource(BookCommentResource, '/bookcomment/')
book_api.add_resource(PopularBookResource, '/popular/')

