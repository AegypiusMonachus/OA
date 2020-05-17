from flask import request, g, current_app
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
from app.gateway.gsrkGW import *
from app.models import db
from app.models.common.utils import *
from app.models.user import User
from app.models.member import Member, MemberPersonalInfo
from app.models.member_level import MemberLevel
from app.models.bank_account import Bank, SystemBankAccount, MemberBankAccount
from app.models.sysadmin_online import SysadminOnline
from app.models.member_account_change import MemberAccountChangeRecord, Deposit
from app.models.memeber_history import OperationHistory
from app.models.dictionary import Dictionary
from app.common.utils import *
from ..common import *
from ..common.utils import *
from sqlalchemy import func
from app.models.memeber_history import *
class MemberDepositStatus(Resource):
	def get(self):
		return {
			1: '申请充值',
			2: '已经入款',
			3: '已经取消',
		}


class MemberDeposits(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'type': fields.Integer,
		'orderId': fields.String,
		'memberId': fields.Integer,
		'memberBankId': fields.Integer,
		'memberUsername': fields.String,
		'memberLevel': fields.Integer,
		'memberLevelName': fields.String,
		'memberBankName': fields.String,
		'memberType': fields.String,
		'memberBankAccountNumber': fields.String,
		'memberBankAccountName': fields.String,
		'systemBankId': fields.Integer,
		'systemBankName': fields.String,
		'systemBankAccountNumber': fields.String,
		'systemBankAccountName': fields.String,
		'systemBankAccountSubbranchName': fields.String,
		'isDelete': fields.Integer,
		'applicationAmount': fields.Float,
		'applicationTime': fields.Integer,
		'depositAmount': fields.Float,
		'depositTime': fields.Integer,
		'status': fields.Integer,
		'auditUsername': fields.String,
		'auditTime': fields.Integer,
		'auditHost': fields.Integer,
		'remitter': fields.String,
		'havediscount': fields.Integer
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

		parser.add_argument('id', type=int)
		parser.add_argument('orderId', type=str)
		parser.add_argument('number', type=int)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('memberLevelId', type=str, dest='memberLevelConfig')
		parser.add_argument('applicationTimeLower', type=int)
		parser.add_argument('applicationTimeUpper', type=int)
		parser.add_argument('auditUsername', type=str)
		parser.add_argument('auditTimeLower', type=int)
		parser.add_argument('auditTimeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('status', type=str)
		parser.add_argument('bankName', type=str)
		parser.add_argument('bankAccountNumber', type=str)
		parser.add_argument('bankAccountName', type=str)
		parser.add_argument('bankAccountSubbranchName', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		criterion.add(Deposit.type.in_([100001, 100003]))
		if args['id']:
			criterion.add(Deposit.id == args['id'])
		if args['number']:
			criterion.add(Deposit.number == args['number'])
		if args['orderId']:
			criterion.add(Deposit.number == args['orderId'])
		if args['applicationTimeLower']:
			criterion.add(Deposit.applicationTime >= args['applicationTimeLower'])
		if args['applicationTimeUpper']:
			criterion.add(Deposit.applicationTime <= args['applicationTimeUpper'] + SECONDS_PER_DAY)
		if args['auditTimeLower']:
			criterion.add(Deposit.auditTime >= args['auditTimeLower'])
		if args['auditTimeUpper']:
			criterion.add(Deposit.auditTime <= args['auditTimeUpper'] + SECONDS_PER_DAY)
		if args['amountLower']:
			criterion.add(Deposit.applicationAmount >= args['amountLower'])
		if args['amountUpper']:
			criterion.add(Deposit.applicationAmount <= args['amountUpper'])
		if args['status']:
			criterion.add(Deposit.status.in_(args['status'].split(',')))

		if args['auditUsername']:
			criterion.add(User.username.in_(args['auditUsername'].split(',')))

		if args['memberUsername']:
			criterion.add(Member.username.in_(args['memberUsername'].split(',')))
		if args['memberLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))

		if args['bankName']:
			criterion.add(Bank.name.in_(args['bankName'].split(',')))
		if args['bankAccountNumber']:
			criterion.add(SystemBankAccount.accountNumber.in_(args['bankAccountNumber'].split(',')))
		if args['bankAccountName']:
			criterion.add(SystemBankAccount.accountName.in_(args['bankAccountName'].split(',')))
		if args['bankAccountSubbranchName']:
			criterion.add(SystemBankAccount.subbranchName.in_(args['bankAccountSubbranchName'].split(',')))

		q = db.session.query(Deposit, Member, MemberLevel, SystemBankAccount, Bank, User).order_by(Deposit.applicationTime.desc())
		q = q.outerjoin(Member, Deposit.memberId == Member.id)
		q = q.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
		q = q.outerjoin(SystemBankAccount, Deposit.systemBankAccountId == SystemBankAccount.id)
		q = q.outerjoin(Bank, SystemBankAccount.bankId == Bank.id)
		q = q.outerjoin(User, Deposit.auditUser == User.id)

		result = []
		pagination = paginate(q, criterion, args['page'], args['pageSize'])
		for item in pagination.items:
			member_bank = Bank.query.get(item.Deposit.bankAccountId) if item.Deposit.bankAccountId else None
			result.append({
				'id': item.Deposit.id,
				'type': item.Deposit.type,
				'orderId': item.Deposit.number,
				'memberId':item.Deposit.memberId,
				'memberType':item.Member.type,
				'memberBankId': item.Deposit.memberId,
				'memberUsername': item.Member.username,
				'memberLevel': item.MemberLevel.id if item.MemberLevel else None,
				'memberLevelName': item.MemberLevel.levelName if item.MemberLevel else None,
				'memberBankName': member_bank.name if member_bank else None,
				'memberBankAccountNumber': None,
				'memberBankAccountName': None,
				'systemBankId':item.Deposit.systemBankAccountId,
				'systemBankName': item.Bank.name if item.Bank else None,
				'systemBankAccountNumber': item.SystemBankAccount.accountNumber if item.SystemBankAccount else None,
				'systemBankAccountName': item.SystemBankAccount.accountName if item.SystemBankAccount else None,
				'systemBankAccountSubbranchName': item.SystemBankAccount.subbranchName if item.SystemBankAccount else None,
				'isDelete': item.SystemBankAccount.isDelete if item.SystemBankAccount else None,
				'applicationAmount': item.Deposit.applicationAmount,
				'applicationTime': item.Deposit.applicationTime,
				'depositAmount': item.Deposit.depositAmount,
				'depositTime': item.Deposit.depositTime,
				'status': item.Deposit.status,
				'auditUsername': item.User.username if item.User else None,
				'auditTime': item.Deposit.auditTime,
				'auditHost': item.Deposit.auditHost,
				'remitter': item.Deposit.remitter,
			})
		if args['orderId']:
			result[0]['havediscount'] = db.session.query(func.count(MemberAccountChangeRecord.accountChangeType)).filter(MemberAccountChangeRecord.accountChangeType == 100010,MemberAccountChangeRecord.orderId == args['orderId']).first()[0]

		return make_response(result, page=pagination.page, pages=pagination.pages, total=pagination.total)

	def post(self):
		# 充值申请类型100001
		# 充值完成类型100003
		parser = RequestParser(trim=True)
		parser.add_argument('username', type=str, required=True)
		parser.add_argument('amount', type=float, required=True)
		parser.add_argument('type', type=int, default=100001)
		parser.add_argument('systemBankAccountId', type=int, required=True)
		args = parser.parse_args(strict=True)

		member = Member.query.filter(Member.username == args.pop('username')).first()
		if not member:
			abort(400)

		deposit = Deposit()
		deposit.status = 1
		deposit.type = args['type']
		deposit.applicationAmount = args['amount']
		deposit.applicationTime = time_to_value()
		deposit.applicationHost = host_to_value(request.remote_addr)
		deposit.auditTime = time_to_value()
		deposit.systemBankAccountId = args['systemBankAccountId']
		deposit.memberId = member.id
		deposit.username = member.username

		with Deposit.lock:
			deposit.number = Deposit.generate_number()
			try:
				db.session.add(deposit)
				db.session.commit()
				OperationHistory().PublicMeDatasApply(100003, deposit)
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)
		return make_response([]), 201

	def put(self,orderId):

		parser = RequestParser(trim=True)
		parser.add_argument('status', type=int, required=True)
		parser.add_argument('amount', type=float)
		parser.add_argument('remark', type=str)
		parser.add_argument('isAcdemen', type=int)
		args = parser.parse_args(strict=True)
		deposit = Deposit.query.filter(Deposit.number == orderId).first()
		mid = OperationHistory().getMemberAll(deposit.memberId)
		if mid.status == 2:
			return {"success":False,"errorMsg":"该用户已被冻结"}
		GW = GsrkGW()
		h_GW = GW.setContext(orderId)
		GW.orderid = orderId
		GW.porderid = orderId
		GW.amount = args['amount']
		try:

			if args['status'] == 2:
				h_sign = GW.accountChange(100003, 0, 0)
				if h_sign:
					OperationHistory().PublicData(100003,deposit)
					return {'messages':'充值成功','success':True}
				else:
					return {'errorMsg':'充值失败','success':False}
			if args['status'] == 99:
				deposit.auditUser = g.current_user.id
				deposit.auditTime = time_to_value()
				deposit.auditHost = host_to_value(request.remote_addr)
				deposit.status = args['status']
			db.session.add(deposit)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])


class ExportMemberDeposits(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('id', type=int)
		parser.add_argument('number', type=int)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('memberLevelId', type=str, dest='memberLevelConfig')
		parser.add_argument('applicationTimeLower', type=int)
		parser.add_argument('applicationTimeUpper', type=int)
		parser.add_argument('auditUsername', type=str)
		parser.add_argument('auditTimeLower', type=int)
		parser.add_argument('auditTimeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('status', type=str)
		parser.add_argument('bankName', type=str)
		parser.add_argument('bankAccountNumber', type=str)
		parser.add_argument('bankAccountName', type=str)
		parser.add_argument('bankAccountSubbranchName', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		criterion.add(Deposit.type.in_([100001, 100003]))
		if args['id']:
			criterion.add(Deposit.id == args['id'])
		if args['number']:
			criterion.add(Deposit.number == args['number'])
		if args['applicationTimeLower']:
			criterion.add(Deposit.applicationTime >= args['applicationTimeLower'])
		if args['applicationTimeUpper']:
			criterion.add(Deposit.applicationTime <= args['applicationTimeUpper'] + SECONDS_PER_DAY)
		if args['auditTimeLower']:
			criterion.add(Deposit.auditTime >= args['auditTimeLower'])
		if args['auditTimeUpper']:
			criterion.add(Deposit.auditTime <= args['auditTimeUpper']  + SECONDS_PER_DAY)
		if args['amountLower']:
			criterion.add(Deposit.applicationAmount >= args['amountLower'])
		if args['amountUpper']:
			criterion.add(Deposit.applicationAmount <= args['amountUpper'])
		if args['status']:
			criterion.add(Deposit.status.in_(args['status'].split(',')))

		if args['auditUsername']:
			criterion.add(User.username.in_(args['auditUsername'].split(',')))

		if args['memberUsername']:
			criterion.add(Member.username.in_(args['memberUsername'].split(',')))
		if args['memberLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))

		if args['bankName']:
			criterion.add(Bank.name.in_(args['bankName'].split(',')))
		if args['bankAccountNumber']:
			criterion.add(SystemBankAccount.accountNumber.in_(args['bankAccountNumber'].split(',')))
		if args['bankAccountName']:
			criterion.add(SystemBankAccount.accountName.in_(args['bankAccountName'].split(',')))
		if args['bankAccountSubbranchName']:
			criterion.add(SystemBankAccount.subbranchName.in_(args['bankAccountSubbranchName'].split(',')))

		q = db.session.query(Deposit, Member, MemberLevel, SystemBankAccount, Bank, User).order_by(
			Deposit.applicationTime.desc())
		q = q.outerjoin(Member, Deposit.memberId == Member.id)
		q = q.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
		q = q.outerjoin(SystemBankAccount, Deposit.systemBankAccountId == SystemBankAccount.id)
		q = q.outerjoin(Bank, SystemBankAccount.bankId == Bank.id)
		q = q.outerjoin(User, Deposit.auditUser == User.id)

		results = []
		items = q.filter(*criterion).all()
		for item in items:
			member_bank = Bank.query.get(item.Deposit.bankAccountId) if item.Deposit.bankAccountId else None
			results.append([
				item.Deposit.number,
				item.Member.username,
				item.MemberLevel.levelName if item.MemberLevel else None,
				member_bank.name if member_bank else None,
				item.Deposit.remitter,
				item.Deposit.pay_type,
				item.Deposit.applicationTime,
				item.Deposit.applicationTime,
				item.Bank.name if item.Bank else None,
				item.SystemBankAccount.accountName if item.SystemBankAccount else None,
				item.SystemBankAccount.subbranchName if item.SystemBankAccount else None,
				item.SystemBankAccount.accountNumber if item.SystemBankAccount else None,
				item.Deposit.depositAmount,
				item.Deposit.status,
				item.User.username if item.User else None,
				item.Deposit.auditTime,
			])
		style = db.session.query(Dictionary.code,Dictionary.name).filter(Dictionary.remark == "公司入款 - 类型").all()
		from openpyxl import Workbook
		import os, time
		workbook = Workbook()
		worksheet = workbook.active
		title = ['订单号', '会员', '会员等级', '存款银行', '存款人', '存款方式', '存款时间', '申请时间',
				  '入款银行', '收款人', '网点', '银行帐号', '金额', '状态', '处理人员','处理时间']
		worksheet.append(title)
		for result in results:
			for s in style:
				if result[5] == s[0]:
					result[5] = s[1]
			st1 = time.localtime(result[6])
			t1 = time.strftime('%Y-%m-%d %H:%M:%S', st1)
			result[6] = t1
			st2 = time.localtime(result[7])
			t2 = time.strftime('%Y-%m-%d %H:%M:%S', st2)
			result[7] = t2
			if result[13] == 1:
				result[13] = "申请中"
			elif result[13] == 2:
				result[13] = "成功到账"
			elif result[13] == 99:
				result[13] = "审核失败"
			if result[15] is not None:
				st3 = time.localtime(result[15])
				t3 = time.strftime('%Y-%m-%d %H:%M:%S', st3)
				result[15] = t3
			worksheet.append(result)

		filename = '公司入款审核-' + str(int(time.time())) + '.xlsx'
		workbook.save(os.path.join(current_app.static_folder, filename))
		return make_response([{
			'success': True,
			'resultFilename': filename,
		}])


class MemberOnlinePayments(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'type': fields.Integer,
		'orderId': fields.String,
		'applicationAmount': fields.Float,
		'applicationTime': fields.Integer,
		'depositAmount': fields.Float,
		'Preferentialamount': fields.Float,
		'depositTime': fields.Integer,
		'status': fields.Integer,
		'auditUsername': fields.String,
		'auditTime': fields.Integer,
		'auditHost': fields.Integer,
		'remitter': fields.String,
		'workId': fields.Integer,
		'workName': fields.String,
		'SysadminOnlineId': fields.Integer,
		'SysadminOnlineName': fields.String,
		'isDelete': fields.Integer,
		'MemberId': fields.Integer,
		'MemberUsername': fields.String,
		'memberType': fields.String,
		'levelId': fields.Integer,
		'levelName': fields.String,
		'havediscount': fields.Integer
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

		parser.add_argument('id', type=int)
		parser.add_argument('orderId', type=str)
		parser.add_argument('MemberUsername', type=str)
		parser.add_argument('applicationTimeLower', type=int)
		parser.add_argument('applicationTimeUpper', type=int)
		parser.add_argument('auditUsername', type=str)
		parser.add_argument('auditTimeLower', type=int)
		parser.add_argument('auditTimeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('status', type=str)
		parser.add_argument('SysadminOnlineName', type=str)
		parser.add_argument('levelId', type=str)
		parser.add_argument('workName', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		criterion.add(Deposit.type.in_([100004]))
		if args['id']:
			criterion.add(Deposit.id == args['id'])
		if args['orderId']:
			criterion.add(Deposit.number == args['orderId'])
		if args['applicationTimeLower']:
			criterion.add(Deposit.applicationTime >= args['applicationTimeLower'])
		if args['applicationTimeUpper']:
			criterion.add(Deposit.applicationTime <= args['applicationTimeUpper'] + SECONDS_PER_DAY)
		if args['auditTimeLower']:
			criterion.add(Deposit.auditTime >= args['auditTimeLower'])
		if args['auditTimeUpper']:
			criterion.add(Deposit.auditTime <= args['auditTimeUpper'] + SECONDS_PER_DAY)
		if args['amountLower']:
			criterion.add(Deposit.applicationAmount >= args['amountLower'])
		if args['amountUpper']:
			criterion.add(Deposit.applicationAmount <= args['amountUpper'])
		if args['status']:
			criterion.add(Deposit.status.in_(args['status'].split(',')))
		if args['auditUsername']:
			criterion.add(User.username.in_(args['auditUsername'].split(',')))
		if args['MemberUsername']:
			criterion.add(Member.username.in_(args['MemberUsername'].split(',')))
		if args['levelId']:
			criterion.add(Member.levelConfig.in_(args['levelId'].split(',')))
		if args['SysadminOnlineName']:
			criterion.add(SysadminOnline.name.in_(args['SysadminOnlineName'].split(',')))
		if args['workName']:
			criterion.add(User.username.in_(args['workName'].split(',')))
		q = db.session.query(
			Deposit.id,
			Deposit.type,
			Deposit.number.label('orderId'),
			Deposit.applicationAmount,
			Deposit.applicationTime,
			Deposit.depositAmount,
			Deposit.depositTime,
			Deposit.status,
			Deposit.auditTime,
			Deposit.auditHost,
			Deposit.remitter,
			User.id.label('workId'),
			User.username.label('workName'),
			SysadminOnline.id.label('SysadminOnlineId'),
			SysadminOnline.name.label('SysadminOnlineName'),
			SysadminOnline.isDelete.label('isDelete'),
			Member.id.label('MemberId'),
			Member.username.label('MemberUsername'),
			Member.type.label('memberType'),
			MemberLevel.id.label('levelId'),
			MemberLevel.levelName.label('levelName')
		).order_by(Deposit.applicationTime.desc())
		q = q.outerjoin(User, Deposit.auditUser == User.id)
		q = q.outerjoin(SysadminOnline, SysadminOnline.id == Deposit.systemBankAccountId)
		q = q.outerjoin(Member, Deposit.username == Member.username)
		q = q.outerjoin(MemberLevel, MemberLevel.id == Member.levelConfig)

		result = []
		pagination = paginate(q, criterion, args['page'], args['pageSize'])
		pagination = convert_pagination(pagination)


		if args['orderId']:
			# pagination.items[0]['havediscount'] = db.session.query(
			# 	func.count(MemberAccountChangeRecord.accountChangeType)
			# ).filter(
			# 	MemberAccountChangeRecord.accountChangeType == 100011,
			# 	MemberAccountChangeRecord.orderId == args['orderId']
			# ).first()[0]
			if pagination.items:
				havediscount = db.session.query(
					func.count(MemberAccountChangeRecord.accountChangeType)
				).filter(
					MemberAccountChangeRecord.accountChangeType == 100011,
					MemberAccountChangeRecord.orderId == args['orderId']
				).first()
				if havediscount is not None:
					havediscount = havediscount[0]
				else:
					havediscount = 0
				pagination.items[0]['havediscount'] = havediscount

		return make_response_from_pagination(pagination)


	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('username', type=str, required=True)
		parser.add_argument('applicationAmount', type=float, required=True)
		parser.add_argument('type', type=int, default=100002)
		parser.add_argument('systemBankAccountId', type=int, required=True)
		args = parser.parse_args(strict=True)

		member = Member.query.filter(Member.username == args.pop('username')).first()
		if not member:
			abort(400)

		deposit = Deposit(**args)
		deposit.status = 1
		deposit.type = args['type']
		deposit.applicationTime = time_to_value()
		deposit.applicationHost = host_to_value(request.remote_addr)
		deposit.auditTime = time_to_value()
		deposit.systemBankAccountId = args['systemBankAccountId']
		deposit.memberId = member.id
		deposit.username = member.username
		with Deposit.lock:
			deposit.number = Deposit.generate_number()
			try:
				db.session.add(deposit)
				db.session.commit()
				OperationHistory().PublicMeDatasApply(100004, deposit)
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)
		return make_response([]), 201

	def put(self,orderId):

		parser = RequestParser(trim=True)
		parser.add_argument('status', type=int, required=True)
		parser.add_argument('amount', type=float)
		parser.add_argument('remark', type=str)
		args = parser.parse_args(strict=True)
		deposit = Deposit.query.filter(Deposit.number == orderId).first()
		mid = OperationHistory().getMemberAll(deposit.memberId)
		if mid.status == 2:
			return {"success": False, "errorMsg": "该用户已被冻结"}
		GW = GsrkGW()
		h_GW = GW.setContext(orderId)
		GW.orderid = orderId
		if deposit.pOrderid:
			GW.porderid = deposit.pOrderid
		else :
			GW.porderid = orderId
		GW.amount = args['amount']
		try:
			if args['status'] == 2:
				h_sign = GW.accountChange(100004, 0, 0)
				if h_sign:
					OperationHistory().PublicData(100004, deposit)
					return {'messages':'充值成功','success':True}
				else:
					return {'errorMsg':'充值失败','success':False}
			if args['status'] == 99 or args['status'] == 3:
				deposit = Deposit.query.filter(Deposit.number == orderId).first()
				deposit_status = deposit.status
				if deposit_status != 1:
					return {'errorMsg':'状态错误','success':False}
				else:
					deposit.auditUser = g.current_user.id
					deposit.auditTime = time_to_value()
					deposit.auditHost = host_to_value(request.remote_addr)
					deposit.status = args['status']
			db.session.add(deposit)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])


class ExportMemberOnlinePayments(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('id', type=int)
		parser.add_argument('orderId', type=str)
		parser.add_argument('MemberUsername', type=str)
		parser.add_argument('applicationTimeLower', type=int)
		parser.add_argument('applicationTimeUpper', type=int)
		parser.add_argument('auditUsername', type=str)
		parser.add_argument('auditTimeLower', type=int)
		parser.add_argument('auditTimeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('status', type=str)
		parser.add_argument('SysadminOnlineName', type=str)
		parser.add_argument('levelId', type=str)
		parser.add_argument('workName', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		criterion.add(Deposit.type.in_([100004]))
		if args['id']:
			criterion.add(Deposit.id == args['id'])
		if args['orderId']:
			criterion.add(Deposit.number == args['orderId'])
		if args['applicationTimeLower']:
			criterion.add(Deposit.applicationTime >= args['applicationTimeLower'])
		if args['applicationTimeUpper']:
			criterion.add(Deposit.applicationTime <= args['applicationTimeUpper'] + SECONDS_PER_DAY)
		if args['auditTimeLower']:
			criterion.add(Deposit.auditTime >= args['auditTimeLower'])
		if args['auditTimeUpper']:
			criterion.add(Deposit.auditTime <= args['auditTimeUpper'] + SECONDS_PER_DAY)
		if args['amountLower']:
			criterion.add(Deposit.applicationAmount >= args['amountLower'])
		if args['amountUpper']:
			criterion.add(Deposit.applicationAmount <= args['amountUpper'])
		if args['status']:
			criterion.add(Deposit.status.in_(args['status'].split(',')))
		if args['auditUsername']:
			criterion.add(User.username.in_(args['auditUsername'].split(',')))
		if args['MemberUsername']:
			criterion.add(Member.username.in_(args['MemberUsername'].split(',')))
		if args['levelId']:
			criterion.add(Member.levelConfig.in_(args['levelId'].split(',')))
		if args['SysadminOnlineName']:
			criterion.add(SysadminOnline.name.in_(args['SysadminOnlineName'].split(',')))
		if args['workName']:
			criterion.add(User.username.in_(args['workName'].split(',')))
		q = db.session.query(Deposit, Member, MemberLevel, SysadminOnline, User).order_by(
			Deposit.applicationTime.desc())
		q = q.outerjoin(User, Deposit.auditUser == User.id)
		q = q.outerjoin(SysadminOnline, SysadminOnline.id == Deposit.systemBankAccountId)
		q = q.outerjoin(Member, Deposit.username == Member.username)
		q = q.outerjoin(MemberLevel, MemberLevel.id == Member.levelConfig)

		results = []
		items = q.filter(*criterion).all()
		for item in items:
			results.append([
				item.Deposit.number,
				item.Member.username,
				item.MemberLevel.levelName if item.MemberLevel else None,
				item.Deposit.applicationTime,
				item.Deposit.applicationAmount,
				0,
				0,
				item.Deposit.status,
				item.Deposit.auditTime,
				item.SysadminOnline.name,
				item.User.username if item.User else None,
			])

		from openpyxl import Workbook
		import os, time
		workbook = Workbook()
		worksheet = workbook.active
		title = ['订单号', '会员', '会员等级', '填写时间', '金额', '手续费', '手续费类型',
				 '状态', '状态更新时间', '商户', '操作人员']
		worksheet.append(title)
		for result in results:
			st1 = time.localtime(result[3])
			t1 = time.strftime('%Y-%m-%d %H:%M:%S', st1)
			result[3] = t1
			if result[7] == 1:
				result[7] = "申请中"
			elif result[7] == 2:
				result[7] = "成功"
			elif result[7] == 99:
				result[7] = "已取消"
			st2 = time.localtime(result[8])
			t2 = time.strftime('%Y-%m-%d %H:%M:%S', st2)
			result[8] = t2
			worksheet.append(result)

		filename = '线上支付-' + str(int(time.time())) + '.xlsx'
		workbook.save(os.path.join(current_app.static_folder, filename))
		return make_response([{
			'success': True,
			'resultFilename': filename,
		}])


class GetMemberDeposits(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

		parser.add_argument('id', type=int)
		parser.add_argument('number', type=int)
		parser.add_argument('orderId', type=str)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('memberLevelId', type=str, dest='memberLevelConfig')
		parser.add_argument('applicationTimeLower', type=int)
		parser.add_argument('applicationTimeUpper', type=int)
		parser.add_argument('auditUsername', type=str)
		parser.add_argument('auditTimeLower', type=int)
		parser.add_argument('auditTimeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('status', type=str)
		parser.add_argument('bankName', type=str)
		parser.add_argument('bankAccountNumber', type=str)
		parser.add_argument('bankAccountName', type=str)
		parser.add_argument('bankAccountSubbranchName', type=str)
		args = parser.parse_args(strict=True)
		criterion = set()
		criterion.add(Deposit.type.in_([100003]))
		if args['id']:
			criterion.add(Deposit.id == args['id'])
		if args['number']:
			criterion.add(Deposit.number == args['number'])
		if args['orderId']:
			criterion.add(Deposit.number == args['orderId'])
		if args['applicationTimeLower']:
			criterion.add(Deposit.applicationTime >= args['applicationTimeLower'])
		if args['applicationTimeUpper']:
			criterion.add(Deposit.applicationTime <= args['applicationTimeUpper'] + SECONDS_PER_DAY)
		if args['auditTimeLower']:
			criterion.add(Deposit.auditTime >= args['auditTimeLower'])
		if args['auditTimeUpper']:
			criterion.add(Deposit.auditTime <= args['auditTimeUpper'] + SECONDS_PER_DAY)
		if args['amountLower']:
			criterion.add(Deposit.applicationAmount >= args['amountLower'])
		if args['amountUpper']:
			criterion.add(Deposit.applicationAmount <= args['amountUpper'])
		if args['status']:
			criterion.add(Deposit.status.in_(args['status'].split(',')))

		if args['auditUsername']:
			criterion.add(User.username.in_(args['auditUsername'].split(',')))

		if args['memberUsername']:
			criterion.add(Member.username.in_(args['memberUsername'].split(',')))
		if args['memberLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))

		if args['bankName']:
			criterion.add(Bank.name.in_(args['bankName'].split(',')))
		if args['bankAccountNumber']:
			criterion.add(SystemBankAccount.accountNumber.in_(args['bankAccountNumber'].split(',')))
		if args['bankAccountName']:
			criterion.add(SystemBankAccount.accountName.in_(args['bankAccountName'].split(',')))
		if args['bankAccountSubbranchName']:
			criterion.add(SystemBankAccount.subbranchName.in_(args['bankAccountSubbranchName'].split(',')))

		countNum = db.session.query(func.count(Deposit.id)).filter(*criterion).all()[0][0]
		accountNum = db.session.query(func.sum(Deposit.applicationAmount)).filter(*criterion).all()[0][0]
		q = db.session.query(
			func.count(Deposit.id),
			func.sum(Deposit.applicationAmount)
		)
		q = q.outerjoin(User, Deposit.auditUser == User.id)
		q = q.outerjoin(SysadminOnline, SysadminOnline.id == Deposit.systemBankAccountId)
		q = q.outerjoin(Member, Deposit.username == Member.username)
		q = q.outerjoin(MemberLevel, MemberLevel.id == Member.levelConfig)
		m_args_list = q.filter(*criterion).all()
		countNum_one = m_args_list[0][0]
		accountNum_one = m_args_list[0][1]
		data = {}
		data['countNum'] = countNum_one
		data['accountNum'] = accountNum_one
		return make_response(data)

class GetMemberOnlinePayments(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

		parser.add_argument('id', type=int)
		parser.add_argument('number', type=int)
		parser.add_argument('orderId', type=str)
		parser.add_argument('MemberUsername', type=str)
		parser.add_argument('applicationTimeLower', type=int)
		parser.add_argument('applicationTimeUpper', type=int)
		parser.add_argument('auditUsername', type=str)
		parser.add_argument('auditTimeLower', type=int)
		parser.add_argument('auditTimeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('status', type=str)
		parser.add_argument('SysadminOnlineName', type=str)
		parser.add_argument('levelId', type=str)
		parser.add_argument('workName', type=str)
		args = parser.parse_args(strict=True)
		criterion = set()
		criterion.add(Deposit.type.in_([100004]))
		if args['id']:
			criterion.add(Deposit.id == args['id'])
		if args['number']:
			criterion.add(Deposit.number == args['number'])
		if args['orderId']:
			criterion.add(Deposit.number == args['orderId'])
		if args['applicationTimeLower']:
			criterion.add(Deposit.applicationTime >= args['applicationTimeLower'])
		if args['applicationTimeUpper']:
			criterion.add(Deposit.applicationTime <= args['applicationTimeUpper'] + SECONDS_PER_DAY)
		if args['auditTimeLower']:
			criterion.add(Deposit.auditTime >= args['auditTimeLower'])
		if args['auditTimeUpper']:
			criterion.add(Deposit.auditTime <= args['auditTimeUpper'] + SECONDS_PER_DAY)
		if args['amountLower']:
			criterion.add(Deposit.applicationAmount >= args['amountLower'])
		if args['amountUpper']:
			criterion.add(Deposit.applicationAmount <= args['amountUpper'])
		if args['status']:
			criterion.add(Deposit.status.in_(args['status'].split(',')))
		if args['auditUsername']:
			criterion.add(User.username.in_(args['auditUsername'].split(',')))
		if args['MemberUsername']:
			criterion.add(Member.username.in_(args['MemberUsername'].split(',')))
		if args['levelId']:
			criterion.add(Member.levelConfig.in_(args['levelId'].split(',')))
		if args['SysadminOnlineName']:
			criterion.add(SysadminOnline.name.in_(args['SysadminOnlineName'].split(',')))
		if args['workName']:
			criterion.add(User.username.in_(args['workName'].split(',')))
		countNum = db.session.query(func.count(Deposit.id)).filter(*criterion).all()[0][0]
		accountNum = db.session.query(func.sum(Deposit.applicationAmount)).filter(*criterion).all()[0][0]
		q = db.session.query(
			func.count(Deposit.id),
			func.sum(Deposit.applicationAmount)
		)
		q = q.outerjoin(User, Deposit.auditUser == User.id)
		q = q.outerjoin(SysadminOnline, SysadminOnline.id == Deposit.systemBankAccountId)
		q = q.outerjoin(Member, Deposit.username == Member.username)
		q = q.outerjoin(MemberLevel, MemberLevel.id == Member.levelConfig)
		m_args_list = q.filter(*criterion).all()
		countNum_one =m_args_list[0][0]
		accountNum_one = m_args_list[0][1]

		data = {}
		data['countNum'] = countNum_one
		data['accountNum'] = accountNum_one
		return make_response(data)


class MemberAccountChange(Resource):
	def put(self,orderId):
		parser = RequestParser(trim=True)
		parser.add_argument('isAcdemen', type=int)
		parser.add_argument('type', type=int)
		args = parser.parse_args(strict=True)
		type_args = args['type']
		del args['type']

		# 管理密码再次确认有待处理
		# password = args.pop('auditUserPassword')
		# user = User.query.get(g.current_user.id)
		# if not user or not user.verify_password(password):
		# 	return jsonify({
		# 		'success': False,
		# 		'errorCode': 403,
		# 		'errorMsg': '密码验证失败'
		# 	})
		try:
			Deposit.query.filter(Deposit.number == orderId).update(args)
			if type_args == 100001:
				MemberAccountChangeRecord.query.filter(MemberAccountChangeRecord.orderId == orderId,MemberAccountChangeRecord.accountChangeType == 100001).update(args)
			if type_args == 100002:
				MemberAccountChangeRecord.query.filter(MemberAccountChangeRecord.orderId == orderId,MemberAccountChangeRecord.accountChangeType == 100002).update(args)

			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return make_response([])


