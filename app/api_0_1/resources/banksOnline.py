from flask_restful import Resource, marshal_with, fields
from ..parsers.systemConfig import bank_online_parsers
from app.models.bank_online import BankOnline
from flask_restful.reqparse import RequestParser
from ..common.utils import *
import datetime
class BanksOnlineAPI(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'name': fields.String,
		"accounts_url" : fields.String,
		"logo_url" : fields.String,
		"pay_url" : fields.String,
		"nodify_url" : fields.String,
		"return_url" : fields.String,
		"pay_type" : fields.String,
		"remark" : fields.String,
		"enable" : fields.Integer,
		"modify_time": fields.String,
	}))
	def get(self,id=None):
		m_args = bank_online_parsers.parse_args(strict=True)
		m_result = BankOnline().getData(id, m_args['page'],m_args['pageSize'],m_args['grade'])
		return make_response(data=m_result[0], page=m_result[1], pages=m_result[2], total=m_result[3])
	
	def post(self):
		pass

	def put(self, id):
		pass

class PaymentGatewayAPI(Resource):

	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('name', type=str)
		args = parser.parse_args(strict=True)
		m_res = BankOnline().getMapList(args['name'])
		return {
			'data': m_res,
			'success':True,
		}
	
