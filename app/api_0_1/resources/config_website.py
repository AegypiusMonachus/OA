from flask_restful import Resource, marshal_with, fields, abort
from app.api_0_1.common.utils import make_marshal_fields, make_response_from_pagination, make_response
from ..parsers.systemConfig import configWebsite
from app.models.config_website import ConfigWebsite, WebsiteSetting
from app.models.config_member_service import ConfigMemberService
from app.models.member import Member
from flask_restful.reqparse import RequestParser
from ..common import *
from app.models.common.utils import *

'''
系统设置 - 站台系统值设置
'''
fields1 = make_marshal_fields({
	'id': fields.Integer,
	'webName': fields.String,
	'agentName': fields.String,
	'loginVerified': fields.Integer,
	'regVerified': fields.Integer,
	'regQAVerified': fields.Integer,
	'errorCount': fields.Integer,
	'puzzleVerifiedLogin': fields.Integer,
	'puzzleVerifiedReg': fields.Integer,
	'landingAreaVerification': fields.Integer,
})


class ConfigWebsiteAPI(Resource):

	@marshal_with(fields1)
	def get(self, id=None):
		criterion = set()
		if id:
			criterion.add(ConfigWebsite.id == id)
		m_rom = ConfigWebsite()
		pagination = m_rom.getData(criterion)
		res = make_response_from_pagination(pagination)
		return res

	def put(self, id):
		m_args = configWebsite.parse_args(strict=True)
		del m_args['page']
		del m_args['pageSize']
		m_res = ConfigWebsite().update(id, **m_args)
		return {'success': True}, 201

'''
系统设置 - 网站设定
'''
class WebsiteSettings(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'name': fields.String,
		'website': fields.String,
		'defAgentId': fields.Integer,
		'defAgentName': fields.String,
		'memberServiceId': fields.Integer,
		'regExamine': fields.Integer,
		'remark': fields.String,
		'memberServiceName': fields.String,
	}))
	def get(self, id=None):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
		args = parser.parse_args(strict=True)

		criterion = set()
		if id:
			criterion.add(WebsiteSetting.id == id)
		pagination = paginate(WebsiteSetting.query, criterion, args['page'], args['pageSize'])
		result = []
		for item in pagination.items:
			if item.memberServiceId:
				memberService = ConfigMemberService.query.filter(ConfigMemberService.id == item.memberServiceId).first()
			result.append({
				'id': item.id,
				'name': item.name,
				'website': item.website,
				'defAgentId': item.defAgentId,
				'defAgentName': item.defAgentName,
				'memberServiceId': item.memberServiceId,
				'regExamine': item.regExamine,
				'remark': item.remark,
				'memberServiceName': memberService.name,
			})
		return make_response(result, page=pagination.page, pages=pagination.pages, total=pagination.total)

	# def post(self):
	# 	parser = RequestParser(trim=True)
	# 	parser.add_argument('name', type=str)
	# 	parser.add_argument('website', type=str)
	# 	parser.add_argument('defAgentId', type=int)
	# 	parser.add_argument('defAgentName', type=str)
	# 	parser.add_argument('memberServiceId', type=int)
	# 	parser.add_argument('regExamine', type=str)
	# 	parser.add_argument('remark', type=str)
	# 	args = parser.parse_args(strict=True)
	#
	# 	try:
	# 		websitesetting = WebsiteSetting(**args)
	# 		db.session.add(websitesetting)
	# 		db.session.commit()
	# 	except:
	# 		db.session.rollback()
	# 		db.session.remove()
	# 		abort(500)
	# 	return make_response([]), 201

	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('defAgentName', type=str)
		parser.add_argument('memberServiceId', type=int)
		parser.add_argument('regExamine', type=str)
		parser.add_argument('remark', type=str)
		args = parser.parse_args(strict=True)

		agents = Member.query.filter(Member.username == args['defAgentName']).first()
		if not agents or agents.type == 0:
			return make_response(error_message='预设代理帐号不存在')

		try:
			websitesetting = WebsiteSetting.query.get(id)
			websitesetting.defAgentId = agents.id
			websitesetting.defAgentName = args['defAgentName']
			websitesetting.memberServiceId = args['memberServiceId']
			websitesetting.regExamine = args['regExamine']
			websitesetting.remark = args['remark']

			db.session.add(websitesetting)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])

	# def delete(self, id):
	# 	websitesetting = WebsiteSetting.query.filter(WebsiteSetting.id == id).first()
	# 	if websitesetting:
	# 		try:
	# 			db.session.delete(websitesetting)
	# 			db.session.commit()
	# 		except:
	# 			db.session.rollback()
	# 			db.session.remove()
	# 			abort(500)
	# 	return {'success': True}, 201

