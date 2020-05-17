from flask import request, g
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser

from app.models.common.utils import *
from app.models.member import *
from app.models.member_level import *
from app.models.config_fanhui import *
from app.models.user import User
from app.models.bank_account import Bank
from app.common.utils import *
from ..common import *
from ..common.utils import *
from app.models.memeber_history import OperationHistory

class AgentAudits(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'status': fields.Integer,
		'applicationTime': fields.Integer,
		'applicationHost': fields.Integer,
		'auditUsername': fields.String,
		'auditTime': fields.Integer,
		'auditHost': fields.Integer,
		'remark': fields.String,
		'username': fields.String,
		'name': fields.String,
		'phone': fields.String,
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
		parser.add_argument('id', type=int)
		parser.add_argument('status', type=str)
		parser.add_argument('username', type=str)
		parser.add_argument('name', type=str)
		parser.add_argument('phone', type=str)
		parser.add_argument('applicationTimeLower', type=int)
		parser.add_argument('applicationTimeUpper', type=int)
		parser.add_argument('auditUsername', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		if args['id']:
			criterion.add(AgentAudit.id == args['id'])
		if args['status']:
			criterion.add(AgentAudit.status.in_(args['status'].split(',')))
		if args['applicationTimeLower']:
			criterion.add(AgentAudit.applicationTime >= args['applicationTimeLower'])
		if args['applicationTimeUpper']:
			criterion.add(AgentAudit.applicationTime <= args['applicationTimeUpper'] + SECONDS_PER_DAY)
		if args['username']:
			criterion.add(AgentAudit.username.in_(args['username'].split(',')))
		if args['name']:
			criterion.add(AgentAudit.personinfo_name == args['name'])
		if args['phone']:
			criterion.add(AgentAudit.personinfo_phone == args['phone'])
		if args['auditUsername']:
			criterion.add(User.username == args['auditUsername'])

		query = db.session.query(
			AgentAudit.id,
			AgentAudit.username,
			AgentAudit.status,
			AgentAudit.applicationTime,
			AgentAudit.applicationHost,
			AgentAudit.auditTime,
			AgentAudit.auditHost,
			AgentAudit.personinfo_name.label('name'),
			AgentAudit.personinfo_phone.label('phone'),
			AgentAudit.remark
		).order_by(AgentAudit.applicationTime.desc())
		query = query.add_column(User.username.label('auditUsername'))
		query = query.outerjoin(User, AgentAudit.auditUser == User.id)

		pagination = paginate(query, criterion, args['page'], args['pageSize'])
		pagination = convert_pagination(pagination)
		return make_response_from_pagination(pagination)

	# def post(self):
	# 	parser = RequestParser(trim=True)
	# 	parser.add_argument('memberId', type=int, required=True)
	# 	args = parser.parse_args(strict=True)
	# 	args['status'] = 1
	# 	args['source'] = request.referrer
	# 	args['applicationTime'] = time_to_value()
	# 	args['applicationHost'] = host_to_value(request.remote_addr)
	# 	try:
	# 		db.session.add(AgentAudit(**args))
	# 		db.session.commit()
	# 		OperationHistory().PublicMemberDatasApply(2002, args['memberId'])
	# 	except:
	# 		db.session.rollback()
	# 		db.session.remove()
	# 		abort(500)
	# 	return make_response([]), 201

	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('agentName', type=str)
		parser.add_argument('defaultRebateConfig', type=int)
		parser.add_argument('defaultLevelConfig', type=int)
		parser.add_argument('rebateRate', type=float)
		parser.add_argument('status', type=int)
		parser.add_argument('remark', type=str)
		args = parser.parse_args(strict=True)
		try:
			audit = AgentAudit.query.get(id)
			if not audit:
				return make_response(error_code=400, error_message="该代理审核不存在")
			if args['remark']:
				audit.remark = args['remark']
			if args['status'] == 2:
				if not args['agentName']:
					return make_response(error_code=400, error_message="请选择总代理")
				if not args['defaultRebateConfig']:
					return make_response(error_code=400, error_message="预设返水不能为空")
				if not args['defaultLevelConfig']:
					return make_response(error_code=400, error_message="预设等级不能为空")
				agent = Member.query.filter(Member.username == args['agentName'], Member.type == 9).first()
				if not agent:
					return make_response(error_code=400, error_message="总代理不存在")
				if agent is not None:
					if args['rebateRate']:
						m_boolean = args['rebateRate'] <= agent.rebateRate or args['rebateRate'] == 0
						if not m_boolean:
							return make_response(error_code=400,error_message="返点率不能超过" + str(float(agent.rebateRate)) + "%")
					else:
						return make_response(error_code=400, error_message="请设置返点")

				try:
					parents = agent.parents + ',%s' % agent.id
					parentsInfo = agent.parentsInfo + ',%s' % agent.username
					member = {}
					member['username'] = audit.username
					member['parent'] = agent.id
					member['parents'] = parents
					member['parentsInfo'] = parentsInfo
					member['passwordHash'] = audit.password
					member['fundPasswordHash'] = audit.coinPassword
					member['type'] = 1
					member['name'] = audit.personinfo_name
					member['registrationTime'] = time_to_value()
					member['agentsTime'] = time_to_value()
					member['registrationHost'] = host_to_value(request.remote_addr)
					member['rebateRate'] = args['rebateRate']
					member['levelConfig'] = agent.defaultLevelConfig
					member['defaultLevelConfig'] = args['defaultLevelConfig']
					member['rebateConfig'] = agent.defaultRebateConfig
					member['defaultRebateConfig'] = args['defaultRebateConfig']
					member['commissionConfig'] = agent.commissionConfig
					member = Member(**member)
					db.session.add(member)
					db.session.commit()

					try:

						personinfo = {}
						personinfo['id'] = member.id
						personinfo['name'] = audit.personinfo_name
						personinfo['gender'] = audit.personinfo_gender
						personinfo['birthdate'] = audit.personinfo_birthdate
						personinfo['phone'] = audit.personinfo_phone
						personinfo['email'] = audit.personinfo_email
						personinfo['tencentQQ'] = audit.personinfo_tencentQQ
						personinfo['tencentWeChat'] = audit.personinfo_tencentWeChat
						personinfo['remark'] = audit.personinfo_remark
						personinfo = MemberPersonalInfo(**personinfo)
						if audit.bank_Id or audit.bank_accountNumber or audit.bank_accountName or audit.bank_province or audit.bank_city:
							agent_bank = {}
							agent_bank['memberId'] = member.id
							agent_bank['bankId'] = audit.bank_Id
							agent_bank['accountNumber'] = audit.bank_accountNumber
							agent_bank['accountName'] = audit.bank_accountName
							agent_bank['province'] = audit.bank_province
							agent_bank['city'] = audit.bank_city
							agent_bank['createTime'] = time_to_value()
							agent_bank = MemberBankAccount(**agent_bank)

							agent_bank_modification_logs = {}
							agent_bank_modification_logs['userId'] = g.current_user.id
							agent_bank_modification_logs['memberId'] = member.id
							agent_bank_modification_logs['bankId'] = audit.bank_Id
							agent_bank_modification_logs['accountNumber'] = audit.bank_accountNumber
							agent_bank_modification_logs['accountName'] = audit.bank_accountName
							agent_bank_modification_logs['province'] = audit.bank_province
							agent_bank_modification_logs['city'] = audit.bank_city
							agent_bank_modification_logs['time'] = time_to_value()

							agent_bank_modification_logs = MemberBankAccountModificationLog(**agent_bank_modification_logs)
							db.session.add(agent_bank)
							db.session.add(agent_bank_modification_logs)
						db.session.add(personinfo)
						# print(1/0)
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

				audit.status = args['status']
				audit.auditUser = g.current_user.id
				audit.auditTime = time_to_value()
				audit.auditHost = host_to_value(request.remote_addr)
				audit.memberId = member.id
				db.session.add(audit)
			elif args['status'] == 3:
				audit.status = args['status']
				audit.auditUser = g.current_user.id
				audit.auditTime = time_to_value()
				audit.auditHost = host_to_value(request.remote_addr)
				db.session.add(audit)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])

class AgentAuditDetails(Resource):

	def get(self, id):
		audit = db.session.query(
			AgentAudit.id.label('id'),
			AgentAudit.memberId.label('memberId'),
			AgentAudit.status.label('status'),
			AgentAudit.source.label('source'),
			AgentAudit.applicationTime.label('applicationTime'),
			AgentAudit.applicationHost.label('applicationHost'),
			AgentAudit.auditTime.label('auditTime'),
			AgentAudit.auditHost.label('auditHost'),
			AgentAudit.remark.label('remark'),
			AgentAudit.username.label('username'),
			User.username.label('auditUsername'),
			AgentAudit.personinfo_name.label('name'),
			AgentAudit.personinfo_gender.label('gender'),
			AgentAudit.personinfo_phone.label('phone'),
			AgentAudit.personinfo_email.label('email'),
			AgentAudit.personinfo_birthdate.label('birthdate'),
			AgentAudit.personinfo_tencentWeChat.label('tencentWeChat'),
			AgentAudit.personinfo_tencentQQ.label('tencentQQ'),
			Bank.name.label('Bankname'),
			AgentAudit.bank_province.label('province'),
			AgentAudit.bank_city.label('city'),
			AgentAudit.bank_accountNumber.label('accountNumber'),
			AgentAudit.bank_accountName.label('bankAccountName')
		).filter(AgentAudit.id == id)
		audit = audit.outerjoin(User, User.id == AgentAudit.auditUser)
		audit = audit.outerjoin(Bank, Bank.id == AgentAudit.bank_Id)
		audit = audit.first()
		if not audit:
			abort(400)
		result = {
			'id': audit.id,
			'memberId': audit.memberId,
			'status': audit.status,
			'source': audit.source,
			'applicationTime': audit.applicationTime,
			'applicationHost': audit.applicationHost,
			'auditUsername': audit.auditUsername,
			'auditTime': audit.auditTime,
			'auditHost': audit.auditHost,
			'remark': audit.remark,
			'username': audit.username,
			'name': audit.name,
			'gender': audit.gender,
			'birthdate': audit.birthdate,
			'phone': audit.phone,
			'email': audit.email,
			'tencentQQ': audit.tencentQQ,
			'tencentWeChat': audit.tencentWeChat,
			'bankName': audit.Bankname,
			'bankAccountNumber': audit.accountNumber,
			'bankAccountName': audit.bankAccountName,
			'province': audit.province,
			'city':audit.city,
		}
		if result['status'] == 2:
			agent = db.session.query(
				Member.parent.label('agentId'),
				Member.rebateRate.label('rebateRate'),
				MemberLevel.levelName.label('defaultLevelConfig'),
				ConfigFanshui.name.label('defaultRebateConfig'),
			).filter(Member.id == result['memberId'])
			agent = agent.outerjoin(MemberLevel, MemberLevel.id == Member.defaultLevelConfig)
			agent = agent.outerjoin(ConfigFanshui, ConfigFanshui.id == Member.defaultRebateConfig)
			agent = agent.first()
			if not agent:
				abort(400)
			agentName = db.session.query(Member.username).filter(Member.id == agent.agentId).first()
			if not agentName:
				abort(400)
			result['zongAgent'] = agentName[0]
			result['defaultRebateConfig'] = agent.defaultRebateConfig
			result['defaultLevelConfig'] = agent.defaultLevelConfig
			result['rebateRate'] = float(agent.rebateRate)
		if result['applicationHost'] is not None:
			result['applicationHost'] = value_to_host(result['applicationHost'])
		if result['auditHost'] is not None:
			result['auditHost'] = value_to_host(result['auditHost'])
		return make_response([result])
