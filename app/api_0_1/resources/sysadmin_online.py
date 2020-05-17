from flask_restful import Resource, marshal_with, fields,abort
from flask_restful.reqparse import RequestParser
from app.api_0_1.common.utils import make_response,make_marshal_fields
from .. import api
from app.api_0_1.parsers.systemConfig import sysadminBank_parsers,sysadminBank_parsers_post
from app.models.sysadmin_online import SysadminOnline
from app.models.member_level import *
from sqlalchemy import func
from flask import request, g
import json,re
from flask_restful.reqparse import RequestParser
from app.models.memeber_history import OperationHistory



'''
公司入款
'''
fields = make_marshal_fields({
		'id': fields.Integer,
		'uid': fields.Integer,
		'name':fields.String,
		'bank_online_id':fields.Integer,
		'enable': fields.Integer,
		'username': fields.String,
		'gradeList': fields.String,
		'code': fields.String,
		'secret_key': fields.String,
		'tb': fields.String,
		'amount': fields.Float,
		'accumulatedAmount': fields.Float,
		'min_amount': fields.Float,
		'max_amount': fields.Float,
		'validTime': fields.Integer,
		'remark': fields.String,
		'RecommendAmount': fields.String,
		'RecommendRemark': fields.String,
		'pay_type': fields.Integer,
# 		'bank':fields.Nested({
#         	'id': fields.Integer,
#          	'name':fields.String,
#          	'home':fields.String,
#     	})
    })

class SysadminOnlineAPI(Resource):
	@marshal_with(fields)	
	def get(self, id=None): 
		m_args = sysadminBank_parsers.parse_args(strict=True)
		criterion = set()
		if id:
			criterion.add(SysadminOnline.id == id)
		if m_args['pay_type']:
			criterion.add(SysadminOnline.pay_type == m_args['pay_type'])
		if m_args['enable'] ==1 or m_args['enable'] == 0:
			criterion.add(SysadminOnline.enable == m_args['enable'])
		if m_args['gradeList']:
			criterion.add(func.find_in_set(m_args['gradeList'],SysadminOnline.gradeList,SysadminOnline.isDelete == 0))

		m_rom = SysadminOnline()
		page = m_rom.getData(criterion, m_args['page'], m_args['pageSize'])
		if page is None:
			return {'data': []}
		return {
			'data': page.items,
			'pages': page.pages,
			'pageNum': page.page,
			'pageSize': len(page.items)
		}
	
	@marshal_with(fields)
	def post(self):
		if not hasattr(g, 'current_member'):
			return {
			'errorCode': "9999",
			'errorMsg': "用戶未登录",
			'success': False
			}
		m_args = sysadminBank_parsers_post.parse_args(strict=True)
		m_args['uid'] = g.current_user.id;
		m_args['username'] = g.current_user.username;
		del m_args['page']
		del m_args['pageSize']
		m_res = SysadminOnline().insert(**m_args)
		# OperationHistory().SysAndBank(300011, m_args['name'])
		return make_response(data=[m_res], page=1, pages=1, total=1) 
	
	def put(self, id):
		m_args = sysadminBank_parsers.parse_args(strict=True)
		del m_args['page']
		del m_args['pageSize']
		m_res = SysadminOnline().update(id,**m_args)
		return {'success': True}, 201 
	
	def delete(self, id):
		m_res = SysadminOnline().delete(id)
		return {'success': True}, 201



class SysadminSimpleAPI(Resource):
	def get(self):
		result = MemberLevel().getLevels()
		result = dict(result)
		result_list = []
		for key,values in result.items():
			result_one = {}
			result_one['id'] = key
			result_one['name'] = values
			result_list.append(result_one)
		# return make_response(result_list, page=1, pages=1, total=1)

		result = {
			"success": True,
			"data": result_list
		}
		return result


