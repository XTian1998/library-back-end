from flask_restful import Api

from App.apis.reader.reader_api import ReaderResource

reader_api = Api(prefix='/reader')
reader_api.add_resource(ReaderResource, '/')