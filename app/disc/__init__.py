from flask import Blueprint
disc_blueprint = Blueprint('disc', __name__)

@disc_blueprint.before_request
def before_request():
	pass

@disc_blueprint.after_request
def after_request(response):
	return response

from flask_restful import Api
api = Api(disc_blueprint)

#from .resources.pay import PayAPI
#api.add_resource(PayAPI, '/pay')

from app.api_0_1.resources.pay import PayAPI
api.add_resource(PayAPI, '/pay/paymentgateway','/pay/<int:id>')

from app.api_0_1.resources.pay import MemberRecharge
api.add_resource(MemberRecharge, '/recharge','/recharge/<int:id>')

from app.api_0_1.resources.withdrawals import CheckDML
api.add_resource(CheckDML, '/checkdml')

from app.api_0_1.resources.withdrawals import Qksq
api.add_resource(Qksq, '/qksq')


