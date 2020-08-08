from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

from App.utils import filename_transfer, admin_login_required

parse = reqparse.RequestParser()
parse.add_argument("file", type=FileStorage, required=True, help="请提供image", location=['files'])


class BookImageResource(Resource):

    @admin_login_required
    def post(self):
        args = parse.parse_args()

        upload = args.get("file")

        file_info = filename_transfer(upload.filename)

        filepath = file_info[0]
        upload.save(filepath)

        data = {
            "data": {
                "url": file_info[1]
            },
            "meta": {
                "status": 200,
                "msg": "上传成功"
            }
        }
        return data