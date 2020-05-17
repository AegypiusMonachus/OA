from flask import request, g, current_app
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
import uuid,time

from sqlalchemy import func

from app.models import db
from app.models.common.utils import *
from app.models.user import User
from app.models.member import Member, MemberPersonalInfo
from app.models.member_level import MemberLevel
from app.models.bank_account import Bank, MemberBankAccount
from app.models.member_account_change import MemberAccountChangeRecord, Withdrawal
from app.common.utils import *
from ..common import *
from ..common.utils import *
from operator import itemgetter

from app.models.memeber_history import OperationHistory

class MemberWithdrawalStatus(Resource):
	def get(self):
		return {
			1: '申请提现',
			2: '已经出款',
			3: '已经退回',
			4: '已经拒绝',
		}


class MemberWithdrawals(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'type': fields.Integer,
		'orderId':fields.String,
		'applicationAmount': fields.Float,
		'applicationTime': fields.Integer,
		'handlingCharge': fields.Float,
		'administrativeCharge': fields.Float,
		'discountCharge': fields.Float,
		'withdrawalAmount': fields.Float,
		'status': fields.Integer,
		'auditUsername': fields.String,
		'auditTime': fields.Integer,
		'auditHost': fields.Integer,
		'remarkFront': fields.String,
		'remark': fields.String,
		'memberId': fields.Integer,
		'memberUsername': fields.String,
		'memberType': fields.String,
		'memberParentUsername': fields.String,
		'memberLevelName': fields.String,
		'memberName': fields.String,
		'memberPhone': fields.String,
		'memberBankName': fields.String,
		'memberBankAccountNumber': fields.String,
		'memberBankAccountName': fields.String,
		'memberBankAccountProvince': fields.String,
		'memberBankAccountCity': fields.String,
		'sxf': fields.Float,
		'yhkc': fields.Float,
		'xzf': fields.Float,
		'isDangerLevel': fields.Integer,
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
		parser.add_argument('id', type=int)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('orderId', type=str)
		parser.add_argument('memberLevelId', type=str, dest='memberLevelConfig')
		parser.add_argument('applicationTimeLower', type=int)
		parser.add_argument('applicationTimeUpper', type=int)
		parser.add_argument('auditUsername', type=str)
		parser.add_argument('auditTimeLower', type=int)
		parser.add_argument('auditTimeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('status', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		criterion.add(Withdrawal.type == 200001)
		if args['id']:
			criterion.add(Withdrawal.id == args['id'])

		if args['orderId']:
			criterion.add(Withdrawal.orderID == args['orderId'])
		if args['applicationTimeLower']:
			criterion.add(Withdrawal.applicationTime >= args['applicationTimeLower'])
		if args['applicationTimeUpper']:
			criterion.add(Withdrawal.applicationTime <= args['applicationTimeUpper'] + SECONDS_PER_DAY)
		if args['auditTimeLower']:
			criterion.add(Withdrawal.auditTime >= args['auditTimeLower'])
		if args['auditTimeUpper']:
			criterion.add(Withdrawal.auditTime <= args['auditTimeUpper'] + SECONDS_PER_DAY)
		if args['amountLower']:
			criterion.add(Withdrawal.applicationAmount >= args['amountLower'])
		if args['amountUpper']:
			criterion.add(Withdrawal.applicationAmount <= args['amountUpper'])
		if args['status']:
			criterion.add(Withdrawal.status.in_(args['status'].split(',')))

		if args['memberUsername']:
			criterion.add(Member.username.in_(args['memberUsername'].split(',')))
		if args['memberLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))

		if args['auditUsername']:
			criterion.add(User.username.in_(args['auditUsername'].split(',')))

		# 日志使用示例
		# 在日志中记录文本信息
		# 在日志中记录预料之内的异常
		# 在日志中记录预料之内的异常的完整堆栈信息
		# 在日志中记录预料之外的异常

		query = db.session.query(
			Withdrawal,
			Member,
			MemberPersonalInfo,
			MemberLevel,
			MemberBankAccount,
			Bank,
			User
		).order_by(Withdrawal.applicationTime.desc())
		query = query.outerjoin(Member, Withdrawal.memberId == Member.id)
		query = query.outerjoin(MemberPersonalInfo, MemberPersonalInfo.id == Member.id)
		query = query.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
		query = query.outerjoin(MemberBankAccount, Member.id == MemberBankAccount.memberId)
		query = query.outerjoin(Bank, MemberBankAccount.bankId == Bank.id)
		query = query.outerjoin(User, Withdrawal.auditUser == User.id)
		
		result = []
		pagination = paginate(query, criterion, args['page'], args['pageSize'])
		for item in pagination.items:
			parent = None
			if item.Member.parent:
				parent = Member.query.get(item.Member.parent)
			result.append({
				'id': item.Withdrawal.id,
				'type': item.Withdrawal.type,
				'orderId':item.Withdrawal.orderID,
				'applicationAmount': item.Withdrawal.applicationAmount,
				'applicationTime': item.Withdrawal.applicationTime,
				'handlingCharge': item.Withdrawal.handlingCharge,
				'administrativeCharge': item.Withdrawal.administrativeCharge,
				'discountCharge': item.Withdrawal.discountCharge,
				'withdrawalAmount': item.Withdrawal.withdrawalAmount,
				'status': item.Withdrawal.status,
				'auditUsername': item.User.username if item.User else None,
				'auditTime': item.Withdrawal.auditTime if item.Withdrawal else None,
				'auditHost': item.Withdrawal.auditHost if item.Withdrawal else None,
				'remarkFront': item.Withdrawal.remarkFront if item.Withdrawal else None,
				'remark': item.Withdrawal.remark if item.Withdrawal else None,
				'memberId': item.Member.id if item.Member else None,
				'memberUsername': item.Member.username if item.Member else None,
				'memberType': item.Member.type if item.Member else None,
				'memberParentUsername': parent.username if parent else None,
				'memberLevelName': item.MemberLevel.levelName if item.MemberLevel else None,
				'memberName': item.MemberPersonalInfo.name if item.MemberPersonalInfo else None,
				'memberPhone': item.MemberPersonalInfo.phone if item.MemberPersonalInfo else None,
				'memberBankName': item.Bank.name if item.Bank else None,
				'memberBankAccountNumber': item.MemberBankAccount.accountNumber if item.MemberBankAccount else None,
				'memberBankAccountName': item.MemberBankAccount.accountName if item.MemberBankAccount else None,
				'memberBankAccountProvince': item.MemberBankAccount.province if item.MemberBankAccount else None,
				'memberBankAccountCity': item.MemberBankAccount.city if item.MemberBankAccount else None,
				'sxf':item.Withdrawal.sxf if item.Withdrawal else None,
				'yhkc':item.Withdrawal.yhkc if item.Withdrawal else None,
				'xzf':item.Withdrawal.xzf if item.Withdrawal else None,
				'isDangerLevel': item.MemberLevel.danger if item.MemberLevel else None,
			})

		# res = sorted(result, key=itemgetter('applicationTime'),reverse = True)
		return make_response(result, page=pagination.page, pages=pagination.pages, total=pagination.total)

	# def post(self):
	# 	parser = RequestParser(trim=True)
	# 	parser.add_argument('username', type=str, required=True)
	# 	parser.add_argument('amount', type=float, required=True)
	# 	args = parser.parse_args(strict=True)
	#
	# 	member = Member.query.filter(Member.username == args.pop('username')).first()
	# 	if not member:
	# 		abort(400)
	#
	# 	member_bank_account = member.bankAccount.first()
	# 	if not member_bank_account:
	# 		abort(400)
	#
	# 	withdrawal = Withdrawal()
	# 	withdrawal.status = 1
	# 	withdrawal.type = 200001
	# 	withdrawal.applicationAmount = args['amount']
	# 	withdrawal.orderID = str(uuid.uuid1()) + str(int(time.time()))
	# 	withdrawal.applicationTime = time_to_value()
	# 	withdrawal.applicationHost = host_to_value(request.remote_addr)
	# 	withdrawal.memberId = member.id
	# 	withdrawal.bankId = member_bank_account.bankId
	# 	withdrawal.bankAccountNumber = member_bank_account.accountNumber
	# 	withdrawal.bankAccountName = member_bank_account.accountName
	# 	try:
	# 		db.session.add(withdrawal)
	# 		db.session.commit()
	#
	# 		# 提现申请时，创建交易记录
	# 		member_account_change_record = MemberAccountChangeRecord()
	# 		member_account_change_record.memberId = withdrawal.member.id
	# 		member_account_change_record.memberBalance = withdrawal.member.balance
	# 		member_account_change_record.memberFrozenBalance = withdrawal.member.frozenBalance
	# 		member_account_change_record.amount = withdrawal.applicationAmount
	# 		member_account_change_record.accountChangeType = 200001
	# 		member_account_change_record.time = withdrawal.applicationTime
	# 		member_account_change_record.host = withdrawal.applicationHost
	# 		member_account_change_record.orderId = withdrawal.id
	#
	# 		# 提现申请时，更新会员余额
	# 		# 提现申请时，更新会员冻结余额
	# 		withdrawal.member.balance -= withdrawal.applicationAmount
	# 		withdrawal.member.frozenBalance += withdrawal.applicationAmount
	#
	# 		try:
	# 			db.session.add(member_account_change_record)
	# 			db.session.add(withdrawal)
	# 			db.session.commit()
	# 		except:
	# 			db.session.rollback()
	# 			db.session.remove()
	# 			db.session.delete(withdrawal)
	# 			db.session.commit()
	# 			abort(500)
	# 	except:
	# 		db.session.rollback()
	# 		db.session.remove()
	# 		abort(500)
	# 	return make_response([]), 201

	def put(self):
		parser = RequestParser(trim=True)
		parser.add_argument('status', type=int)
		parser.add_argument('orderId', type=str)
		parser.add_argument('remark', type=str)
		parser.add_argument('remarkFront', type=str)
		args = parser.parse_args(strict=True)

		import re
		if args['remark']:
			remarks = args['remark']
			remarks_a = re.search('^[\u4E00-\u9FA5A-Za-z0-9\\s+]+$', remarks)
			if not remarks_a:
				return make_response(error_code=400, error_message='备注包含非法字符')
		if args['remarkFront']:
			remarkFronts = args['remarkFront']
			remarkFronts_a = re.search('^[\u4E00-\u9FA5A-Za-z0-9\\s+]+$', remarkFronts)
			if not remarkFronts_a:
				return make_response(error_code=400, error_message='备注包含非法字符')

		# 提现审核时，手续费尚需处理
		# 提现审核时，行政费尚需处理
		# 提现审核时，优惠费尚需处理

		withdrawal = Withdrawal.query.filter(Withdrawal.orderID == args['orderId']).first()
		mid = OperationHistory().getMemberAll(withdrawal.memberId)
		if mid.status == 2:
			return {"success": False, "errorMsg": "该用户已被冻结"}
		withdrawal_status = withdrawal.status


		try:

			if withdrawal_status != 1:
				try:
					if args['remark']:
						withdrawal.remark = args['remark']
					if args['remarkFront']:
						withdrawal.remarkFront = args['remarkFront']
					db.session.add(withdrawal)
					db.session.commit()
					return {'success': True}
				except:
					db.session.rollback()
					db.session.remove()
				return {'errorMsg': '状态错误', 'success': False}
			elif args['status']:
				withdrawal.auditUser = g.current_user.id
				withdrawal.auditTime = time_to_value()
				withdrawal.auditHost = host_to_value(request.remote_addr)
				withdrawal.status = args['status']

				if args['status'] == 2:
					# 提现审核通过，已支付，创建交易记录
					member_account_change_record = MemberAccountChangeRecord()
					member_account_change_record.memberId = withdrawal.member.id
					member_account_change_record.memberBalance = withdrawal.member.balance
					member_account_change_record.memberFrozenBalance = withdrawal.member.frozenBalance
					member_account_change_record.amount = -withdrawal.withdrawalAmount
					member_account_change_record.sxf = -(withdrawal.sxf + withdrawal.yhkc + withdrawal.xzf)
					member_account_change_record.accountChangeType = 200002
					member_account_change_record.info = '线上取款通过'
					member_account_change_record.time = withdrawal.auditTime
					member_account_change_record.host = withdrawal.auditHost
					member_account_change_record.orderId = withdrawal.orderID
					member_account_change_record.rechargeid = withdrawal.orderID
					member_account_change_record.actionUID = g.current_user.id
					member_account_change_record.isAcdemen = 1
					db.session.add(member_account_change_record)

					# 提现审核通过，已支付，更新会员余额
					# 提现审核通过，已支付，更新会员打码
					if withdrawal.member.frozenBalance is None:
						withdrawal.member.frozenBalance = 0
					if withdrawal.withdrawalAmount is None:
						withdrawal.withdrawalAmount = 0
					if withdrawal.member.hitCodeNeed is None:
						withdrawal.member.hitCodeNeed = 0
					if withdrawal.withdrawalAmount is None:
						withdrawal.withdrawalAmount = 0
					withdrawal.member.frozenBalance -= withdrawal.applicationAmount
					#withdrawal.member.hitCodeNeed -= withdrawal.withdrawalAmount
					#if withdrawal.yhkc is None:
					#	withdrawal.yhkc = 0
					#if withdrawal.member.discount is None:
					#	withdrawal.member.discount = 0
					#m_int = withdrawal.member.discount - withdrawal.yhkc
					#if m_int < 0:
# 						withdrawal.member.discount = 0
					#else :
					#	withdrawal.member.discount = m_int
					OperationHistory().PublicDatas(200002, withdrawal)
					#删除liqType = 200001且订单号withdrawal.orderID的数据
					m_sql = 'delete from blast_coin_log  where uid = %s and liqType = %s and extfield0 = "%s"'%(withdrawal.member.id,200001,withdrawal.orderID)
					db.session.execute(m_sql)
				if args['status'] == 3:
					# 提现审核未通过，已退回，创建交易记录
					member_account_change_record = MemberAccountChangeRecord()
					member_account_change_record.memberId = withdrawal.member.id
					member_account_change_record.memberBalance = withdrawal.member.balance
					member_account_change_record.memberFrozenBalance = withdrawal.member.frozenBalance
					member_account_change_record.amount = withdrawal.withdrawalAmount
					member_account_change_record.accountChangeType = 200003
					member_account_change_record.info = '线上取款退回'
					member_account_change_record.time = withdrawal.auditTime
					member_account_change_record.host = withdrawal.auditHost
					member_account_change_record.orderId = withdrawal.orderID
					member_account_change_record.rechargeid = withdrawal.orderID
					member_account_change_record.actionUID = g.current_user.id
					member_account_change_record.sxf = withdrawal.sxf+withdrawal.yhkc+withdrawal.xzf
					db.session.add(member_account_change_record)
					
					# 提现审核未通过，已退回，更新会员余额
					# 提现审核未通过，已退回，更新会员冻结余额
					withdrawal.member.frozenBalance -= withdrawal.applicationAmount
					withdrawal.member.balance += withdrawal.applicationAmount
					OperationHistory().PublicDatas(200003, withdrawal)
				if args['status'] == 4:
					member_account_change_record = MemberAccountChangeRecord()
					member_account_change_record.memberId = withdrawal.member.id
					member_account_change_record.memberBalance = withdrawal.member.balance
					member_account_change_record.memberFrozenBalance = withdrawal.member.frozenBalance
					member_account_change_record.amount = -withdrawal.withdrawalAmount
					member_account_change_record.accountChangeType = 200004
					member_account_change_record.info = '线上取款拒绝'
					member_account_change_record.time = withdrawal.auditTime
					member_account_change_record.host = withdrawal.auditHost
					member_account_change_record.orderId = withdrawal.orderID
					member_account_change_record.rechargeid = withdrawal.orderID
					member_account_change_record.actionUID = g.current_user.id
					member_account_change_record.sxf = -(withdrawal.sxf + withdrawal.yhkc + withdrawal.xzf)
					db.session.add(member_account_change_record)
					withdrawal.member.frozenBalance -= withdrawal.applicationAmount
					m_sql = 'delete from blast_coin_log  where uid = %s and liqType = %s and extfield0 = "%s"'%(withdrawal.member.id,200001,withdrawal.orderID)
					db.session.execute(m_sql)
					OperationHistory().PublicDatas(200004, withdrawal)
			if args['remark']:
				withdrawal.remark = args['remark']
			if args['remarkFront']:
				withdrawal.remarkFront = args['remarkFront']
			db.session.add(withdrawal)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])


class ExportMemberWithdrawals(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('id', type=int)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('orderId', type=str)
		parser.add_argument('memberLevelId', type=str, dest='memberLevelConfig')
		parser.add_argument('applicationTimeLower', type=int)
		parser.add_argument('applicationTimeUpper', type=int)
		parser.add_argument('auditUsername', type=str)
		parser.add_argument('auditTimeLower', type=int)
		parser.add_argument('auditTimeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('status', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		criterion.add(Withdrawal.type == 200001)
		if args['id']:
			criterion.add(Withdrawal.id == args['id'])
		if args['orderId']:
			criterion.add(Withdrawal.orderID == args['orderId'])
		if args['applicationTimeLower']:
			criterion.add(Withdrawal.applicationTime >= args['applicationTimeLower'])
		if args['applicationTimeUpper']:
			criterion.add(Withdrawal.applicationTime <= args['applicationTimeUpper'] + SECONDS_PER_DAY)
		if args['auditTimeLower']:
			criterion.add(Withdrawal.auditTime >= args['auditTimeLower'])
		if args['auditTimeUpper']:
			criterion.add(Withdrawal.auditTime <= args['auditTimeUpper'] + SECONDS_PER_DAY)
		if args['amountLower']:
			criterion.add(Withdrawal.applicationAmount >= args['amountLower'])
		if args['amountUpper']:
			criterion.add(Withdrawal.applicationAmount <= args['amountUpper'])
		if args['status']:
			criterion.add(Withdrawal.status.in_(args['status'].split(',')))

		if args['memberUsername']:
			criterion.add(Member.username.in_(args['memberUsername'].split(',')))
		if args['memberLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))

		if args['auditUsername']:
			criterion.add(User.username.in_(args['auditUsername'].split(',')))

		query = db.session.query(
			Withdrawal,
			Member,
			MemberPersonalInfo,
			MemberLevel,
			MemberBankAccount,
			Bank,
			User
		).order_by(Withdrawal.applicationTime.desc())
		query = query.outerjoin(Member, Withdrawal.memberId == Member.id)
		query = query.outerjoin(MemberPersonalInfo, MemberPersonalInfo.id == Member.id)
		query = query.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
		query = query.outerjoin(MemberBankAccount, Member.id == MemberBankAccount.memberId)
		query = query.outerjoin(Bank, MemberBankAccount.bankId == Bank.id)
		query = query.outerjoin(User, Withdrawal.auditUser == User.id)

		results = []
		items = query.filter(*criterion).all()
		for item in items:
			parent = Member.query.get(item.Member.parent)
			results.append([
				item.Withdrawal.orderID,
				None,
				item.Member.username,
				item.MemberPersonalInfo.name if item.MemberPersonalInfo else None,
				item.MemberLevel.levelName,
				item.Bank.name if item.Bank else None,
				item.MemberBankAccount.province if item.MemberBankAccount else None,
				item.MemberBankAccount.city if item.MemberBankAccount else None,
				item.MemberBankAccount.accountNumber if item.MemberBankAccount else None,
				item.Withdrawal.applicationTime,
				item.Withdrawal.withdrawalAmount,
				item.Withdrawal.sxf,
				item.Withdrawal.xzf,
				item.Withdrawal.yhkc,
				item.Withdrawal.applicationAmount,
				item.Withdrawal.status,
				item.User.username if item.User else None,
				item.Withdrawal.auditTime,
				item.Withdrawal.remark,
				None,
				None,
				None
			])

		from openpyxl import Workbook
		import os, time
		workbook = Workbook()
		worksheet = workbook.active
		title = ['订单号', '首次申请取款', '会员', '真实姓名', '会员等级', '银行名称', '省', '县市', '银行帐户',
				  '申请时间', '帐户提出额度', '手续费', '行政费用', '优惠扣除', '出款金额', '状态', '处理人员',
				 '处理时间', '备注', '支付宝帐号', '支付宝昵称', '支付宝备注']
		worksheet.append(title)
		for result in results:
			st1 = time.localtime(result[9])
			t1 = time.strftime('%Y-%m-%d %H:%M:%S', st1)
			result[9] = t1
			if result[15] == 1:
				result[15] = '申请中'
			elif result[15] == 2:
				result[15] = '已出款'
			elif result[15] == 3:
				result[15] = '已退回'
			elif result[15] == 4:
				result[15] = '已拒绝'
			if result[17] is not None:
				st2 = time.localtime(result[17])
				t2 = time.strftime('%Y-%m-%d %H:%M:%S', st2)
				result[17] = t2
			worksheet.append(result)

		filename = '取款申请审核-' + str(int(time.time())) + '.xlsx'
		workbook.save(os.path.join(current_app.static_folder, filename))

		return make_response([{
			'success': True,
			'resultFilename': filename,
		}])


# 取款申请审核搜寻查询人员总笔数和总金额
class SearchMoneyCount(Resource):
	@marshal_with(make_marshal_fields({
		'countNum': fields.Integer,
		'accountNum': fields.String
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
		parser.add_argument('id', type=int)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('orderId', type=str)
		parser.add_argument('memberLevelId', type=str, dest='memberLevelConfig')
		parser.add_argument('applicationTimeLower', type=int)
		parser.add_argument('applicationTimeUpper', type=int)
		parser.add_argument('auditUsername', type=str)
		parser.add_argument('auditTimeLower', type=int)
		parser.add_argument('auditTimeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('status', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		criterion.add(Withdrawal.type == 200001)
		if args['id']:
			criterion.add(Withdrawal.id == args['id'])

		if args['orderId']:
			criterion.add(Withdrawal.orderID == args['orderId'])
		if args['applicationTimeLower']:
			criterion.add(Withdrawal.applicationTime >= args['applicationTimeLower'])
		if args['applicationTimeUpper']:
			criterion.add(Withdrawal.applicationTime <= args['applicationTimeUpper'] + SECONDS_PER_DAY)
		if args['auditTimeLower']:
			criterion.add(Withdrawal.auditTime >= args['auditTimeLower'])
		if args['auditTimeUpper']:
			criterion.add(Withdrawal.auditTime <= args['auditTimeUpper'] + SECONDS_PER_DAY)
		if args['amountLower']:
			criterion.add(Withdrawal.applicationAmount >= args['amountLower'])
		if args['amountUpper']:
			criterion.add(Withdrawal.applicationAmount <= args['amountUpper'])
		if args['status']:
			criterion.add(Withdrawal.status.in_(args['status'].split(',')))

		if args['memberUsername']:
			criterion.add(Member.username.in_(args['memberUsername'].split(',')))
		if args['memberLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))

		if args['auditUsername']:
			criterion.add(User.username.in_(args['auditUsername'].split(',')))

# 		# 日志使用示例
# 		# 在日志中记录文本信息
# 		# 在日志中记录预料之内的异常
# 		# 在日志中记录预料之内的异常的完整堆栈信息
# 		# 在日志中记录预料之外的异常
# 		current_app.logger.info('[EXAMPLE] What a wonderful world.')
# 
# 		try:
# 			raise Exception('[EXAMPLE][EXCEPTION] What a wonderful world.')
# 		except Exception as e:
# 			current_app.logger.error(e)
# 
# 		try:
# 			raise Exception('[EXAMPLE][EXCEPTION][WITH STACK TRACE] What a wonderful world.')
# 		except Exception as e:
# 			current_app.logger.exception(e)

		query = db.session.query(Withdrawal, Member, MemberPersonalInfo, MemberLevel, MemberBankAccount, Bank, User)
		query = query.outerjoin(Member, Withdrawal.memberId == Member.id)
		query = query.outerjoin(MemberPersonalInfo, MemberPersonalInfo.id == Member.id)
		query = query.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
		query = query.outerjoin(MemberBankAccount, Member.id == MemberBankAccount.memberId)
		query = query.outerjoin(Bank, MemberBankAccount.bankId == Bank.id)
		query = query.outerjoin(User, Withdrawal.auditUser == User.id)

		result = []
		pagination = paginate(query, criterion, args['page'], args['pageSize'])
		for item in pagination.items:
			parent = None
			if item.Member.parent:
				parent = Member.query.get(item.Member.parent)
			result.append({
				'id': item.Withdrawal.id,
				'type': item.Withdrawal.type,
				'orderId': item.Withdrawal.orderID,
				'applicationAmount': item.Withdrawal.applicationAmount,
				'applicationTime': item.Withdrawal.applicationTime,
				'handlingCharge': item.Withdrawal.handlingCharge,
				'administrativeCharge': item.Withdrawal.administrativeCharge,
				'discountCharge': item.Withdrawal.discountCharge,
				'withdrawalAmount': item.Withdrawal.withdrawalAmount,
				'status': item.Withdrawal.status,
				'auditUsername': item.User.username if item.User else None,
				'auditTime': item.Withdrawal.auditTime if item.Withdrawal else None,
				'auditHost': item.Withdrawal.auditHost if item.Withdrawal else None,
				'remarkFront': item.Withdrawal.remarkFront if item.Withdrawal else None,
				'remark': item.Withdrawal.remark if item.Withdrawal else None,
				'memberId': item.Member.id if item.Member else None,
				'memberUsername': item.Member.username if item.Member else None,
				'memberParentUsername': parent.username if parent else None,
				'memberLevelName': item.MemberLevel.levelName if item.MemberLevel else None,
				'memberName': item.MemberPersonalInfo.name if item.MemberPersonalInfo else None,
				'memberPhone': item.MemberPersonalInfo.phone if item.MemberPersonalInfo else None,
				'memberBankName': item.Bank.name if item.Bank else None,
				'memberBankAccountNumber': item.MemberBankAccount.accountNumber if item.MemberBankAccount else None,
				'memberBankAccountName': item.MemberBankAccount.accountName if item.MemberBankAccount else None,
				'memberBankAccountProvince': item.MemberBankAccount.province if item.MemberBankAccount else None,
				'memberBankAccountCity': item.MemberBankAccount.city if item.MemberBankAccount else None,
			})
		moneyall = []
		for i in result:
			money = i["applicationAmount"]
			moneyall.append(money)
		moneycount = 0
		for m in moneyall:
			M = m
			moneycount += M
		data = {}
		data['countNum'] = pagination.total
		data['accountNum'] = moneycount
		return make_response(data, page=pagination.page, pages=pagination.pages, total=pagination.total)


class MemberWithdrawalsChange(Resource):
	def put(self,orderId):
		parser = RequestParser(trim=True)
		parser.add_argument('isAcdemen', type=int)
		parser.add_argument('type', type=int)
		args = parser.parse_args(strict=True)
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
			Withdrawal.query.filter(Withdrawal.orderID == orderId).update(args)
			MemberAccountChangeRecord.query.filter(MemberAccountChangeRecord.orderId == orderId,MemberAccountChangeRecord.accountChangeType == 200002).update(args)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return make_response([])



