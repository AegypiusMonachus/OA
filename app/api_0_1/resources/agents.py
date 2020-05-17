import os, sys, re
import time
from sqlalchemy import or_,and_

from flask import request, g, current_app
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
from sqlalchemy import and_
from flask.json import jsonify
from app.models import db
from app.models.common.utils import *
from app.models.member import Member, MemberPersonalInfo
from app.models.member_level import MemberLevel
from app.models.bank_account import Bank, MemberBankAccount, MemberBankAccountModificationLog
from app.models.blast_links import BlastLinks, LinksUser
from app.models.config_system import ConfigSystem
from app.common.utils import *
from ..common import *
from ..common.utils import *

from app.models.memeber_history import OperationHistory

class Agents(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'username': fields.String,
		'name': fields.String,
		'registrationTime': fields.Integer,
		'registrationHost': fields.Integer,
		'status': fields.Integer,
		'type': fields.Integer,
	}))
	def get(self, id=None):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

		parser.add_argument('username', type=str)
		parser.add_argument('registrationTimeLower', type=int)
		parser.add_argument('registrationTimeUpper', type=int)
		parser.add_argument('registrationHost', type=int)
		parser.add_argument('commissionConfig', type=int)
		parser.add_argument('defaultRebateConfig', type=int)
		parser.add_argument('defaultLevelConfig', type=str)
		parser.add_argument('type', type=int)
		parser.add_argument('status', type=int)
		parser.add_argument('rebateConfig', type=int)
		parser.add_argument('parentUsername', type=str)
		parser.add_argument('agentLink', type=str)

		parser.add_argument('name', type=str)
		parser.add_argument('nameLike', type=str)
		parser.add_argument('birthdateLower', type=int)
		parser.add_argument('birthdateUpper', type=int)
		parser.add_argument('gender', type=int)
		parser.add_argument('phone', type=str)
		parser.add_argument('phoneLike', type=str)
		parser.add_argument('email', type=str)
		parser.add_argument('emailLike', type=str)
		parser.add_argument('tencentWeChat', type=str)
		parser.add_argument('tencentWeChatLike', type=str)
		parser.add_argument('tencentQQ', type=str)
		parser.add_argument('tencentQQLike', type=str)

		parser.add_argument('bankAccountNumber', type=str)
		parser.add_argument('bankAccountNumberLike', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		criterion.add(Member.type != 0)
		if id:
			criterion.add(Member.id.in_([id]))
		if args['username']:
			criterion.add(Member.username.in_(args['username'].split(',')))
		if args['registrationTimeLower']:
			criterion.add(Member.agentsTime >= args['registrationTimeLower'])
		if args['registrationTimeUpper']:
			criterion.add(Member.agentsTime <= args['registrationTimeUpper'] + SECONDS_PER_DAY)
		if args['commissionConfig']:
			criterion.add(Member.commissionConfig == args['commissionConfig'])
		if args['defaultRebateConfig']:
			criterion.add(Member.defaultRebateConfig == args['defaultRebateConfig'])
		if args['defaultLevelConfig']:
			criterion.add(Member.defaultLevelConfig.in_(args['defaultLevelConfig'].split(',')))
		if args['type'] is not None:
			criterion.add(Member.type == args['type'])
		if args['status'] is not None:
			criterion.add(Member.status == args['status'])
		if args['parentUsername']:
			parent = Member.query.filter(Member.username == args['parentUsername']).first()
			if parent:
				criterion.add(Member.parent == parent.id)
			else:
				return make_response([])
		if args['agentLink']:
			links = db.session.query(BlastLinks.uid).filter(BlastLinks.link.in_(args['agentLink'].split(','))).all()
			criterion.add(Member.id.in_([link.uid for link in links]))

		if args['name']:
			criterion.add(MemberPersonalInfo.name == args['name'])
		if args['nameLike']:
			criterion.add(MemberPersonalInfo.name.like('%' + args['nameLike'] + '%'))
		if args['birthdateLower']:
			criterion.add(MemberPersonalInfo.birthdate > args['birthdateLower'])
		if args['birthdateUpper']:
			criterion.add(MemberPersonalInfo.birthdate < args['birthdateUpper'])
		if args['gender']:
			criterion.add(MemberPersonalInfo.gender == args['gender'])
		if args['phone']:
			criterion.add(MemberPersonalInfo.phone == args['phone'])
		if args['phoneLike']:
			criterion.add(MemberPersonalInfo.phone.like('%' + args['phoneLike'] + '%'))
		if args['email']:
			criterion.add(MemberPersonalInfo.email == args['email'])
		if args['emailLike']:
			criterion.add(MemberPersonalInfo.email.like('%' + args['emailLike'] + '%'))
		if args['tencentWeChat']:
			criterion.add(MemberPersonalInfo.tencentWeChat == args['tencentWeChat'])
		if args['tencentWeChatLike']:
			criterion.add(MemberPersonalInfo.tencentWeChat.like('%' + args['tencentWeChatLike'] + '%'))
		if args['tencentQQ']:
			criterion.add(MemberPersonalInfo.tencentQQ == args['tencentQQ'])
		if args['tencentQQLike']:
			criterion.add(MemberPersonalInfo.tencentQQ.like('%' + args['tencentQQLike'] + '%'))

		if args['bankAccountNumber']:
			str_args = '''select uid from blast_member_bank where account = {}'''.format(args['bankAccountNumber'])
			uidArray = execute(str_args)[0]
			h_results = []
			for numbers in uidArray:
				h_results.append(numbers[0])
			criterion.add(Member.id.in_(h_results))
		if args['bankAccountNumberLike']:
			str_args = '''select uid from blast_member_bank where account like "%{}%"'''.format(args["bankAccountNumberLike"])
			uidArray = execute(str_args)[0]
			h_results = []
			for numbers in uidArray:
				h_results.append(numbers[0])
			criterion.add(Member.id.in_(h_results))

		q1 = db.session.query(
			Member.id,
			Member.username,
			Member.registrationTime,
			Member.registrationHost,
			Member.status,
			Member.type,
			MemberPersonalInfo
		).order_by(Member.registrationTime.desc())
		q1 = q1.outerjoin(MemberPersonalInfo, Member.id == MemberPersonalInfo.id)

		result = []
		pagination = paginate(q1, criterion, args['page'], args['pageSize'])
		for item in pagination.items:
			result.append({
				'id':item.id,
				'username':item.username,
				'name':item.MemberPersonalInfo.name if item.MemberPersonalInfo else None,
				'registrationTime': item.registrationTime,
				'registrationHost': item.registrationHost,
				'status': item.status,
				'type': item.type
			})
		return make_response(result, page=pagination.page, pages=pagination.pages, total=pagination.total)

	def post(self):
		member_parser = RequestParser(trim=True)
		member_parser.add_argument('username', type=str)
		member_parser.add_argument('password', type=str, default=DEFAULT_MEMBER_PASSWORD)
		member_parser.add_argument('fundPassword', type=str, default=DEFAULT_MEMBER_FUND_PASSWORD)
		member_parser.add_argument('parentUsername', type=str)
		member_parser.add_argument('commissionConfig', type=int)
		member_parser.add_argument('defaultRebateConfig', type=int)
		member_parser.add_argument('defaultLevelConfig', type=int)
		member_parser.add_argument('type', type=int)
		member_parser.add_argument('rebateRate', type=float)
		member_args = member_parser.parse_args()

		member_personal_info_parser = RequestParser(trim=True)
		member_personal_info_parser.add_argument('name', type=str)
		member_personal_info_parser.add_argument('birthdate', type=str)
		member_personal_info_parser.add_argument('gender', type=int)
		member_personal_info_parser.add_argument('phone', type=str)
		member_personal_info_parser.add_argument('email', type=str)
		member_personal_info_parser.add_argument('tencentQQ', type=str)
		member_personal_info_parser.add_argument('tencentWeChat', type=str)
		member_personal_info_parser.add_argument('personalInfoRemark', type=str, dest='remark')
		member_personal_info_args = member_personal_info_parser.parse_args()

		pattern = "^[A-Za-z0-9\\u4e00-\\u9fa5][A-Za-z0-9\\u4e00-\\u9fa5-_]{4,13}[A-Za-z0-9\\u4e00-\\u9fa5]$"
		if member_args['type'] is not None:
			if member_args['type'] == 1:
				re_result = re.match(pattern, member_args['username'])
				if re_result is None:
					return make_response(error_code=400, error_message="账号必须为6-15位字母和数字组合")
		if member_personal_info_args['birthdate'] is None or len(member_personal_info_args['birthdate']) == 0:
			member_personal_info_args['birthdate'] = None
		else:
			timeArray = time.strptime(member_personal_info_args['birthdate'], "%Y-%m-%d")
			timestamp = time.mktime(timeArray)
			member_personal_info_args['birthdate'] = int(timestamp)
		member_personal_info_args = {key: value for key, value in member_personal_info_args.items() if value}

		member_bank_account_parser = RequestParser(trim=True)
		member_bank_account_parser.add_argument('bankId', type=str)
		member_bank_account_parser.add_argument('accountNumber', type=str)
		member_bank_account_parser.add_argument('accountName', type=str)
		member_bank_account_parser.add_argument('subbranchName', type=str)
		member_bank_account_parser.add_argument('province', type=str)
		member_bank_account_parser.add_argument('city', type=str)
		member_bank_account_parser.add_argument('bankAccountRemark', type=str, dest='remark')
		member_bank_account_args = member_bank_account_parser.parse_args()
		if member_args['type'] is None or member_args['type']=='' or  member_args['type']=="":
			return {
				'errorCode': "9998",
				'errorMsg': "代理层级不能为空",
				'success': False
			}
		if member_args['username'] is None or member_args['username']=='' or  member_args['username']=="":
			return {
				'errorCode': "9998",
				'errorMsg': "用户名不能为空",
				'success': False
			}
		if member_args['type'] != 11:
			if member_args['parentUsername'] is None or member_args['parentUsername']=='' or  member_args['parentUsername']=="":
				return {
					'errorCode': "9998",
					'errorMsg': "上层代理不能为空",
					'success': False
				}
		if member_args['commissionConfig'] is None or member_args['commissionConfig']=='' or  member_args['commissionConfig']=="":
			return {
				'errorCode': "9998",
				'errorMsg': "佣金设定不能为空",
				'success': False
			}
		if member_args['type'] == 1:
			if member_args['defaultRebateConfig'] is None or member_args['defaultRebateConfig']=='' or  member_args['defaultRebateConfig']=="":
				return {
					'errorCode': "9998",
					'errorMsg': "预设反水不能为空",
					'success': False
				}
			if member_args['defaultLevelConfig'] is None or member_args['defaultLevelConfig']=='' or  member_args['defaultLevelConfig']=="":
				return {
					'errorCode': "9998",
					'errorMsg': "预设会员等级不能为空",
					'success': False
				}

		if member_args['type'] == 1:

			parent = Member.query.filter(Member.username == member_args['parentUsername'],Member.type==9).first()
			if parent is None:
				return {
				'errorCode': "9998",
				'errorMsg': "上层代理错误",
				'success': False
			}
		if member_args['type'] == 9:
			if 'defaultRebateConfig' in member_args:
				del member_args['defaultRebateConfig']
			if 'defaultLevelConfig' in member_args:
				del member_args['defaultLevelConfig']
			parent = Member.query.filter(Member.username == member_args['parentUsername'],Member.type==10).first()
			if parent is None:
				return {
				'errorCode': "9998",
				'errorMsg': "上层代理错误",
				'success': False
			}
		if member_args['type'] == 10:
			if 'defaultRebateConfig' in member_args:
				del member_args['defaultRebateConfig']
			if 'defaultLevelConfig' in member_args:
				del member_args['defaultLevelConfig']
			parent = Member.query.filter(Member.username == member_args['parentUsername'],Member.type==11).first()
			if parent is None:
				return {
				'errorCode': "9998",
				'errorMsg': "上层代理错误",
				'success': False
			}
		if member_args['type'] == 11:
			if 'defaultRebateConfig' in member_args:
				del member_args['defaultRebateConfig']
			if 'defaultLevelConfig' in member_args:
				del member_args['defaultLevelConfig']
			if member_args['parentUsername'] is not None:
				return {
					'errorCode': "9998",
					'errorMsg': "该级没有上层代理，不可设置",
					'success': False
				}
		if member_bank_account_args['bankId'] is None or len(member_bank_account_args['bankId']) == 0:
			member_bank_account_args['bankId'] = None
		else:
			member_bank_account_args['bankId'] = int(member_bank_account_args['bankId'])
		member_bank_account_args = {key: value for key, value in member_bank_account_args.items() if value}

		member = Member.query.filter(Member.username == member_args['username']).first()
		if member:
			return make_response(error_message='用户名已存在')
		if member_args['parentUsername'] is not None:
			parent = Member.query.filter(Member.username == member_args.pop('parentUsername')).first()
			if parent.status == 0:
				return jsonify({
					'success': False,
					'errorCode': 403,
					'errorMsg': '该代理已被停用'
				})
			if member_args['rebateRate']:
				m_boolean = member_args['rebateRate'] <= parent.rebateRate or member_args['rebateRate']==0
				if not m_boolean:
					return make_response(error_code=400, error_message="返点率不能超过" + str(float(parent.rebateRate)) + "%")
			else:
				return make_response(error_code=400, error_message="请设置返点")
			if member_args['type'] != 11:
				if not parent or not parent.type:
					return make_response(error_message='上级用户名错误')
				if parent.parents is None:
					parents = '%s' % parent.id
					parentsInfo =  '%s' % parent.username
				else:
					parents = parent.parents + ',%s' % parent.id
					parentsInfo = parent.parentsInfo + ',%s' % parent.username
				member_args['parent'] = parent.id
				member_args['parents'] = parents
				member_args['parentsInfo'] = parentsInfo
				member_args['levelConfig'] = parent.defaultLevelConfig
				member_args['rebateConfig'] = parent.defaultRebateConfig
				# #暂时以这种情况新增反水设定
				# member_args['defaultLevelConfig'] = parent.defaultLevelConfig
				# member_args['defaultLevelConfig'] = parent.defaultLevelConfig
			else:
				member_args['parent'] = None
				member_args['parents'] = None
				member_args['parentsInfo'] = None
				member_args['levelConfig'] = None
				member_args['rebateConfig'] = None
		else:
			member_args.pop('parentUsername')

		try:

			member_args['registrationTime'] = time_to_value()
			member_args['agentsTime'] = time_to_value()
			member_args['registrationHost'] = host_to_value(request.remote_addr)
			member = Member(**member_args)

			db.session.add(member)
			db.session.commit()
			OperationHistory().PublicMemberDatasApply(2001, member.id)

			try:
					member_personal_info_args['id'] = member.id
					member_personal_info = MemberPersonalInfo(**member_personal_info_args)


					if any(member_bank_account_args.values()):
						member_bank_account_args['memberId'] = member.id
						member_bank_account = MemberBankAccount(**member_bank_account_args)

						member_bank_account_args['userId'] = g.current_user.id
						member_bank_account_args['time'] = time_to_value()
						member_bank_account_modification_log = MemberBankAccountModificationLog(**member_bank_account_args)

						db.session.add(member_bank_account)
						db.session.add(member_bank_account_modification_log)

					db.session.add(member_personal_info)

					db.session.commit()
					OperationHistory().PublicMemberDatasApply(1002, member.id)
					OperationHistory().PublicMemberDatasApply(1003, member.id)
			except:
				db.session.rollback()
				db.session.remove()
				db.session.delete(member)
				db.session.commit()
				abort(500)
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([]), 201

	@marshal_with(make_marshal_fields({
		'password': fields.String,
		'fundPassword': fields.String,
	}))
	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('password', type=str)
		parser.add_argument('fundPassword', type=str)
		parser.add_argument('status', type=int)
		parser.add_argument('agentLink', type=str)
		parser.add_argument('agentCustomLink', type=str)
		parser.add_argument('commissionConfig', type=int)
		parser.add_argument('defaultRebateConfig', type=int)
		parser.add_argument('defaultLevelConfig', type=int)
		parser.add_argument('rebateRate', type=float)
		parser.add_argument('parentId', type=int)
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value is not None}
		if 'rebateRate' in args and args['rebateRate']:
			parent = Member.query.filter(Member.id == args.pop('parentId'),Member.type != 0).first()
			if not parent or not parent.type:
				return make_response(error_code=400, error_message="该代理不存在,请重新输入")
			m_boolean = args['rebateRate'] <= parent.rebateRate or args['rebateRate']==0
			if not m_boolean:
				return make_response(error_code=400, error_message="返点不正确")
		if 'parentId' in args:
			args.pop('parentId')
		try:
			member = Member.query.get(id)
			if member:
				for key, value in args.items():
					if hasattr(member, key):
						setattr(member, key, value)
				db.session.add(member)
				db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([{
			'password': args.get('password'),
			'fundPassword': args.get('fundPassword')
		}])


class ExportAgents(Resource):
	def get(self, id=None):
		parser = RequestParser(trim=True)

		parser.add_argument('username', type=str)
		parser.add_argument('registrationTimeLower', type=int)
		parser.add_argument('registrationTimeUpper', type=int)
		parser.add_argument('commissionConfig', type=int)
		parser.add_argument('defaultRebateConfig', type=int)
		parser.add_argument('defaultLevelConfig', type=str)
		parser.add_argument('type', type=int)
		parser.add_argument('status', type=int)
		parser.add_argument('parentUsername', type=str)
		parser.add_argument('agentLink', type=str)

		parser.add_argument('name', type=str)
		parser.add_argument('nameLike', type=str)
		parser.add_argument('birthdateLower', type=int)
		parser.add_argument('birthdateUpper', type=int)
		parser.add_argument('gender', type=int)
		parser.add_argument('phone', type=str)
		parser.add_argument('phoneLike', type=str)
		parser.add_argument('email', type=str)
		parser.add_argument('emailLike', type=str)
		parser.add_argument('tencentWeChat', type=str)
		parser.add_argument('tencentWeChatLike', type=str)
		parser.add_argument('tencentQQ', type=str)
		parser.add_argument('tencentQQLike', type=str)

		parser.add_argument('bankAccountNumber', type=str)
		parser.add_argument('bankAccountNumberLike', type=str)
		args = parser.parse_args()

		criterion = set()
		criterion.add(Member.type != 0)
		if id:
			criterion.add(Member.id.in_([id]))
		if args['username']:
			criterion.add(Member.username.in_(args['username'].split(',')))
		if args['registrationTimeLower']:
			criterion.add(Member.registrationTime > args['registrationTimeLower'])
		if args['registrationTimeUpper']:
			criterion.add(Member.registrationTime < args['registrationTimeUpper'] + SECONDS_PER_DAY)
		if args['commissionConfig']:
			criterion.add(Member.commissionConfig == args['commissionConfig'])
		if args['defaultRebateConfig']:
			criterion.add(Member.defaultRebateConfig == args['defaultRebateConfig'])
		if args['defaultLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['defaultLevelConfig'].split(',')))
		if args['type'] is not None:
			criterion.add(Member.status == args['type'])
		if args['status'] is not None:
			criterion.add(Member.status == args['status'])
		if args['parentUsername']:
			parent = Member.query.filter(Member.username == args['parentUsername']).first()
			if parent:
				criterion.add(Member.parent == parent.id)
			else:
				return make_response([])
		if args['agentLink']:
			links = db.session.query(BlastLinks.uid).filter(BlastLinks.link.in_(args['agentLink'].split(','))).all()
			criterion.add(Member.id.in_([link.uid for link in links]))

		if args['name']:
			criterion.add(MemberPersonalInfo.name == args['name'])
		if args['nameLike']:
			criterion.add(MemberPersonalInfo.name.like('%' + args['nameLike'] + '%'))
		if args['birthdateLower']:
			criterion.add(MemberPersonalInfo.birthdate > args['birthdateLower'])
		if args['birthdateUpper']:
			criterion.add(MemberPersonalInfo.birthdate < args['birthdateUpper'])
		if args['gender']:
			criterion.add(MemberPersonalInfo.gender == args['gender'])
		if args['phone']:
			criterion.add(MemberPersonalInfo.phone == args['phone'])
		if args['phoneLike']:
			criterion.add(MemberPersonalInfo.phone.like('%' + args['phoneLike'] + '%'))
		if args['email']:
			criterion.add(MemberPersonalInfo.email == args['email'])
		if args['emailLike']:
			criterion.add(MemberPersonalInfo.email.like('%' + args['emailLike'] + '%'))
		if args['tencentWeChat']:
			criterion.add(MemberPersonalInfo.tencentWeChat == args['tencentWeChat'])
		if args['tencentWeChatLike']:
			criterion.add(MemberPersonalInfo.tencentWeChat.like('%' + args['tencentWeChatLike'] + '%'))
		if args['tencentQQ']:
			criterion.add(MemberPersonalInfo.tencentQQ == args['tencentQQ'])
		if args['tencentQQLike']:
			criterion.add(MemberPersonalInfo.tencentQQ.like('%' + args['tencentQQLike'] + '%'))

		if args['bankAccountNumber']:
			criterion.add(MemberBankAccount.accountNumber == args['bankAccountNumber'])
		if args['bankAccountNumberLike']:
			criterion.add(MemberBankAccount.accountNumber.like('%' + args['bankAccountNumberLike'] + '%'))

		q = db.session.query(Member, MemberPersonalInfo, BlastLinks, LinksUser, MemberBankAccount).order_by(
			Member.registrationTime.desc())
		q = q.outerjoin(MemberPersonalInfo, MemberPersonalInfo.id == Member.id)
		q = q.outerjoin(MemberBankAccount, Member.id == MemberBankAccount.memberId)
		q = q.outerjoin(Bank, MemberBankAccount.bankId == Bank.id)
		q = q.outerjoin(BlastLinks, BlastLinks.uid == Member.id)
		q = q.outerjoin(LinksUser, LinksUser.uid == Member.id)

		items = q.filter(*criterion).all()
		results = []
		for item in items:
			member_bank = Bank.query.get(item.MemberBankAccount.bankId) if item.MemberBankAccount else None
			results.append([
				item.Member.type,
				item.Member.username,
				item.Member.status,
				item.Member.registrationTime,
				item.BlastLinks.link if item.BlastLinks else None,
				item.LinksUser.web_domain if item.LinksUser else None,
				item.MemberPersonalInfo.name if item.MemberPersonalInfo else None,
				item.MemberPersonalInfo.phone if item.MemberPersonalInfo else None,
				item.MemberPersonalInfo.gender if item.MemberPersonalInfo else None,
				item.MemberPersonalInfo.email if item.MemberPersonalInfo else None,
				item.MemberPersonalInfo.birthdate if item.MemberPersonalInfo else None,
				item.MemberPersonalInfo.tencentWeChat if item.MemberPersonalInfo else None,
				item.MemberPersonalInfo.tencentQQ if item.MemberPersonalInfo else None,
				member_bank.name if member_bank else None,
				item.MemberBankAccount.province if item.MemberBankAccount else None,
				item.MemberBankAccount.city if item.MemberBankAccount else None,
				item.MemberBankAccount.accountNumber if item.MemberBankAccount else None,
				item.MemberBankAccount.remark if item.MemberBankAccount else None,
			])

		config_sys = ConfigSystem.query.filter(ConfigSystem.code == '2002').first()
		from openpyxl import Workbook
		workbook = Workbook()
		worksheet = workbook.active
		title = ['层级', '帐号', '状态', '建立时间', '推广链结', '自订推广链结', '真实姓名', '手机', '性别', 'Email',
				 '生日', '微信号', 'QQ', '银行名称', '省份', '县市', '帐户', '备注']
		worksheet.append(title)
		result_name = []
		result_datas = []
		for result in results:
			result_list = list(result)
			if result_list[1] in result_name:
				i = result_name.index(result_list[1])
				result_datas[i][4] = str(result_datas[i][4]) +','+ str(result_list[4])
				result_datas[i][5] = str(result_datas[i][5]) + ',' + str(result_list[5])
				continue
			if result_list[0] == 1:
				result_list[0] = "代理"
			elif result_list[0] == 9:
				result_list[0] = "总代理"
			elif result_list[0] == 10:
				result_list[0] = "股东"
			elif result_list[0] == 11:
				result_list[0] = "大股东"

			if result_list[2] == 1:
				result_list[2] = "启用"
			elif result_list[2] == 0:
				result_list[2] = "禁用"

			st1 = time.localtime(result_list[3])
			result_list[3] = time.strftime('%Y-%m-%d %H:%M:%S', st1)

			if result_list[8] == 1:
				result_list[8] = "女"
			elif result_list[8] == 2:
				result_list[8] = "男"

			if result_list[10] is not None:
				st = time.localtime(result_list[10])
				result_list[10] = time.strftime('%Y-%m-%d %H:%M:%S', st)

			result_name.append(result_list[1])
			result_datas.append(result_list)

		for result_data in result_datas:
			if result_data[4]:
				links = result_data[4].split(',')
				links = list(set(links))
				member_link = ''
				for link in links:
					if link != 'None':
						member_link = member_link + str(config_sys.name) + '?a=' + link + ','
				result_data[4] = member_link[:-1]
			if result_data[5]:
				user_links = result_data[5].split(',')
				user_links = list(set(user_links))
				member_user_link = ''
				for user_link in user_links:
					if user_link != 'None':
						member_user_link = member_user_link + ',' + user_link
				result_data[5] = member_user_link[1:]
			worksheet.append(result_data)
		filename = '代理-' + str(int(time.time())) + '.xlsx'
		workbook.save(os.path.join(current_app.static_folder, filename))

		return make_response([{
			'success': True,
			'resultFilename': filename,
		}])


class DefaultAgents(Resource):
	@marshal_with(make_marshal_fields({
		'username': fields.String,
	}))
	def get(self):
		results = Member.query.filter(Member.type == 9).all()
		return make_response(results)

	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('username', type=str, required=True)
		args = parser.parse_args(strict=True)

		try:
			member = Member()
			member.type = 9
			member.username = args['username']
			member.registrationTime = time_to_value()
			member.registrationHost = host_to_value(request.remote_addr)

			db.session.add(member)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([]), 201

	def put(self):
		parser = RequestParser(trim=True)
		parser.add_argument('username', type=str)
		args = parser.parse_args(strict=True)

		try:
			member = Member.query.filter(Member.type == 9).first()
			if args['username']:
				member.username = args['username']

			db.session.add(member)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])


class AgentPersonalInfos(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'name': fields.String,
		'gender': fields.Integer,
		'birthdate': fields.Integer,
		'phone': fields.String,
		'email': fields.String,
		'tencentQQ': fields.String,
		'tencentWeChat': fields.String,
		'remark': fields.String,
	}))
	def get(self, id):
		member = Member.query.get(id)
		if not member:
			abort(400)
		return make_response(member.personalInfo.all())

	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('name', type=str)
		parser.add_argument('gender', type=int)
		parser.add_argument('birthdate', type=int)
		parser.add_argument('phone', type=str)
		parser.add_argument('email', type=str)
		parser.add_argument('tencentQQ', type=str)
		parser.add_argument('tencentWeChat', type=str)
		args = parser.parse_args(strict=True)

		member = Member.query.get(id)
		if not member:
			abort(400)
		try:
			memberInfo = MemberPersonalInfo.query.get(id)
			if memberInfo:
				MemberPersonalInfo.query.filter(MemberPersonalInfo.id == id).update(args)
			else:
				args['id'] = id
				memberInfo = MemberPersonalInfo(**args)
				db.session.add(memberInfo)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])

class AgentPersonalInfosRemark(Resource):
	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('remark', type=str)
		args = parser.parse_args(strict=True)

		member = Member.query.get(id)
		if not member:
			abort(400)
		try:
			memberInfo = MemberPersonalInfo.query.get(id)
			if memberInfo:
				MemberPersonalInfo.query.filter(MemberPersonalInfo.id == id).update(args)
			else:
				args['id'] = id
				memberInfo = MemberPersonalInfo(**args)
				db.session.add(memberInfo)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])


class AgentDetails(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'username': fields.String,
		'registrationTime': fields.Integer,
		'registrationHost': fields.String,
		'status': fields.Integer,
		'type': fields.Integer,
		'parents': fields.List(fields.Nested({
			'id': fields.Integer,
			'username': fields.String,
			'rebateRate':fields.Float,
		})),
		'commissionConfigName': fields.String,
		'defaultRebateConfig': fields.Integer,
		'commissionConfig': fields.Integer,
		'defaultRebateConfigName': fields.String,
		'defaultlevelConfig': fields.Integer,
		'defaultLevelConfigName': fields.String,
		'agentLink': fields.String,
		'agentCustomLink': fields.String,
		'name': fields.String,
		'phone': fields.String,
		'remark': fields.String,
		'bankId': fields.Integer,
		'bankName': fields.String,
		'bankAccountName': fields.String,
		'bankAccountNumber': fields.String,
		'rebateRate':fields.Float,
	}))
	def get(self, id):
		member = Member.query.get(id)
		if not member:
			return make_response([])
		if member.defaultLevelConfig is not None:
			memberLevel = MemberLevel.query.get(member.defaultLevelConfig)
		else:
			memberLevel = None
		result = {
			'id': member.id,
			'username': member.username,
			'type': member.type,
			'registrationTime': member.registrationTime,
			'registrationHost': value_to_host(member.registrationHost),
			'status': member.status,
			'parents': [],
			'commissionConfig': member.commissionConfig,
			'commissionConfigName': member.commission_config.name if member.commission_config else None,
			'defaultRebateConfig': member.defaultRebateConfig,
			'defaultRebateConfigName': member.default_rebate_config.name if member.default_rebate_config else None,
			'defaultlevelConfig': member.defaultLevelConfig,
			'defaultLevelConfigName': memberLevel.levelName if memberLevel else None,
			'rebateRate':member.rebateRate
		}

		parent_id = member.parent
		while parent_id:
			parent = Member.query.get(parent_id)
			#太尼玛危险了，很可能造成内存泄漏，死循环
			if parent_id == parent.parent:
				break
			if not parent:
				break
			result['parents'].append({'id': parent.id, 'username': parent.username,"rebateRate":parent.rebateRate})
			parent_id = parent.parent

		personal_info = member.personalInfo.first()
		if personal_info:
			result['name'] = personal_info.name
			result['phone'] = personal_info.phone
			result['remark'] = personal_info.remark

		bank_account = member.bankAccount.first()
		if bank_account:
			result['bankId'] = bank_account.bankId
			result['bankName'] = bank_account.bank.name
			result['bankAccountName'] = bank_account.accountName
			result['bankAccountNumber'] = bank_account.accountNumber

		return make_response([result])

# 代理详情页，会员总人数显示
class SearchCountMember(Resource):
	def get(self,id):
		result = {}
		data ={}
		member = Member.query.get(id)
		if member.type == 9:
			agentcount = db.session.query(Member).filter(Member.parent == id,Member.type == 1).count()
			menmbercount = db.session.query(Member).filter(Member.parent == id,Member.type == 1).all()
			a = 0
			for i in menmbercount:
				count = db.session.query(Member).filter(Member.parent == i.id, Member.type == 0,Member.isTsetPLay != 1).count()
				a += count
			data["agentcount"] = agentcount
			data['menmbercount'] = a
			return make_response(data)
		else:
			membercount = db.session.query(Member).filter(Member.parent == id,Member.type == 0,Member.isTsetPLay != 1).count()
			result["menmbercount"] = membercount
			return make_response(result)


class AgentsTotal(Resource):
	def get(self):
		agents = db.session.query(Member.id,Member.username).filter(Member.type == 9).all()
		result = []
		for agent in agents:
			result.append({
				'number':agent.id,
				'username': agent.username,
			})

		return make_response(result)