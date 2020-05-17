from flask import Blueprint
noauth_blueprint = Blueprint('noauth', __name__)

@noauth_blueprint.before_request
def before_request():
    pass


@noauth_blueprint.after_request
def after_request(response):
    return response


from flask_restful import Api
api = Api(noauth_blueprint)


from app.noauth.resources.bibao_notify import BibaoNotify
api.add_resource(BibaoNotify, '/getBankCard','/getBankCard/<int:id>')

from .resources.entertainment_city import (
    EntertainmentCityAPI,
    GameListAPI
)
api.add_resource(EntertainmentCityAPI,'/entertainmentcity')
api.add_resource(GameListAPI,'/entertainmentcity/<string:code>/gamelist')   

from app.api_0_1.resources.pay import SynchorAPI
api.add_resource(SynchorAPI, '/pay/synchor/<string:id>')
from app.api_0_1.resources.pay import NotifyAPI
api.add_resource(NotifyAPI, '/pay/notify/<string:id>')
