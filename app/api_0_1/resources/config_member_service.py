from flask_restful import Resource, marshal_with, fields
from flask_restful.reqparse import RequestParser
from app.api_0_1.common.utils import make_response,make_marshal_fields
from .. import api
from ..parsers.systemConfig import configMemberService_parsers
from app.models.config_member_service import ConfigMemberService
import json

'''
系统设置 - 佣金
'''
fields = make_marshal_fields({
		'id': fields.Integer,
		'name': fields.String,
		'member_reg': fields.String,
		'agent_reg': fields.String,
		'remark': fields.String,
		'pmd': fields.String
    })

'''
会员端设定
'''
class ConfigMemberServiceAPI(Resource):
	
	@marshal_with(fields)	
	def get(self, id=None): 
		m_args = configMemberService_parsers.parse_args(strict=True)
		criterion = set()
		if id:
			criterion.add(ConfigMemberService.id == id)
		m_rom = ConfigMemberService()
		page = m_rom.getData(criterion)
		if page is None:
			return {'data': []}
		return {
			'data': page.items,
			'pages': page.pages,
			'page': page.page,
			'pageSize': len(page.items)
		}
	
	@marshal_with(fields)
	def post(self):
		m_args = configMemberService_parsers.parse_args(strict=True)
		del m_args['page']
		del m_args['pageSize']
		m_res = ConfigMemberService().insert(**m_args)
		return make_response(data=[m_res], page=1, pages=1, total=1) 
	
	def put(self, id):
		m_args = configMemberService_parsers.parse_args(strict=True)
		del m_args['page']
		del m_args['pageSize']
		m_res = ConfigMemberService().update(id,**m_args)
		return {'success': True}, 201 
	
	def delete(self, id):
		m_res = ConfigMemberService().delete(id)
		return {'success': True}, 201 