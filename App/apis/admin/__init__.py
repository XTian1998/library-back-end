from flask_restful import Api

from App.apis.admin.admin_user_api import AdminUserResource
from App.apis.admin.blacklist_manage_api import BlackListResource, BlackUserResource

admin_api = Api(prefix="/admin")

admin_api.add_resource(AdminUserResource, '/adminuser/')
admin_api.add_resource(BlackListResource, '/blacklist/')
admin_api.add_resource(BlackUserResource, '/blackuser/<string:id>/')
