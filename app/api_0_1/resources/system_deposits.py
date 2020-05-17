from flask import request, g, current_app
from flask.json import jsonify
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
from app.common.orderUtils import *
from app.models import db
from app.models.common.utils import *
from app.models.member import Member
from app.models.member_account_change import MemberAccountChangeRecord, Deposit
from app.models.user import User
from app.common.utils import *
from ..common import *
from ..common.utils import *
from app.models.memeber_history import OperationHistory

class SystemDepositTypes(Resource):
	def get(self):
		return [
			{'id': 900001, 'name': '后台提存（入款）'},
			{'id': 900006, 'name': '优惠活动'},
			{'id': 900003, 'name': '补发派奖'},
			{'id': 900004, 'name': '返水'},
			{'id': 900005, 'name': '其他'},
			{'id': 900011, 'name': '转账额度确认'}
		]

class SystemDeposits(Resource):

	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('auditUserPassword', type=str)
		parser.add_argument('username', type=str, required=True)
		parser.add_argument('amount', type=float, required=True)
		parser.add_argument('type', type=int, default=900001)
		parser.add_argument('remarkFront', type=str)
		parser.add_argument('remark', type=str)
		parser.add_argument('auditType', type=int, default=1)
		parser.add_argument('auditCharge', type=float, default=0)
		parser.add_argument('isAcdemen', type=int, default=0)
		args = parser.parse_args(strict=True)

		# 管理密码再次确认有待处理
		password = args.pop('auditUserPassword')
		user = User.query.get(g.current_user.id)
		if not user or not user.verify_password(password):
			return jsonify({
				'success': False,
				'errorCode': 403,
				'errorMsg': '密码验证失败'
			})
		if user.systemDepositLimitOnce is not None:
			if args['amount'] > user.systemDepositLimitOnce:
				return jsonify({
					'success': False,
					'errorCode': 403,
					'errorMsg': '超出单次存款上限'
				})
		if user.systemDepositLimitCount  is not None:
			if user.systemDepositLimitTotal  == None:
				user.systemDepositLimitTotal = 0
			if args['amount'] > user.systemDepositLimitCount - user.systemDepositLimitTotal :
				return jsonify({
					'success': False,
					'errorCode': 403,
					'errorMsg': '超出您的总存入限额'
				})
		try:
			deposits = []
			members = Member.query.filter(Member.username.in_(args['username'].split(',')), Member.status == 2).all()
			if members:
				datas = []
				for member in members:
					datas.append(member.username)
				return {"success": False, "errorMsg": "批次处理的用户中有已被冻结的用户","data":datas}
			else:
				members = Member.query.filter(Member.username.in_(args['username'].split(','))).all()
			for member in members:
				deposit = Deposit()
				deposit.status = 2
				deposit.type = args['type']
				deposit.isAcdemen = args['isAcdemen']
				deposit.memberId = member.id
				deposit.username = member.username
				deposit.applicationAmount = args['amount']
				deposit.applicationTime = time_to_value()
				deposit.applicationHost = host_to_value(request.remote_addr)
				deposit.depositAmount = deposit.applicationAmount
				deposit.depositTime = deposit.applicationTime
				deposit.auditUser = g.current_user.id
				deposit.auditTime = time_to_value()
				deposit.auditHost = host_to_value(request.remote_addr)
				uid = member.id
				deposit.number = createOrderIdNew(uid=uid)

				member_account_change_record = MemberAccountChangeRecord()
				member_account_change_record.memberId = member.id
				member_account_change_record.memberBalance = member.balance + deposit.depositAmount
				member_account_change_record.memberFrozenBalance = member.frozenBalance
				member_account_change_record.amount = deposit.depositAmount
				member_account_change_record.accountChangeType = deposit.type
				if args['type'] == 900001:
					member_account_change_record.info = '人工存入(入款)'
				elif args['type'] == 900006:
					member_account_change_record.info = '优惠活动（入款）'
				elif args['type'] == 900003:
					member_account_change_record.info = '补发派奖（入款）'
				elif args['type'] == 900004:
					member_account_change_record.info = '返水（入款）'
				elif args['type'] == 900005:
					member_account_change_record.info = '其他（入款）'
				member_account_change_record.time = deposit.auditTime
				member_account_change_record.host = deposit.auditHost
				member_account_change_record.actionUID = g.current_user.id
				member_account_change_record.isAcdemen = args['isAcdemen']
				uid = member.id
				member_account_change_record.orderId = deposit.number
				member_account_change_record.rechargeid = deposit.number

				# 存款金额进入会员余额
				# 稽核金额进入会员打码
				if member.balance == None:
					member.balance = 0
				member.balance += args['amount']
				# 更新子账户存入总金额累计
				if user.systemDepositLimitTotal == None:
					user.systemDepositLimitTotal = 0
				user.systemDepositLimitTotal += args['amount']

				# 交易记录中需要记录稽核类型，以便稽核修改
				# 交易记录中需要记录稽核金额，以便稽核修改
				member_account_change_record.auditType = args['auditType']
				member_account_change_record.auditCharge = args['auditCharge']

				# 稽核类型为存款稽核，稽核金额进入会员打码
				# 稽核类型为优惠稽核，稽核金额进入会员打码及会员优惠
				if args['auditType'] == 1:
					pass
				if args['auditType'] == 2:
					if member.hitCodeNeed == None:
						member.hitCodeNeed = 0
					member.hitCodeNeed += args['auditCharge']
				if args['auditType'] == 3:
					if member.hitCodeNeed == None:
						member.hitCodeNeed = 0
					if member.discount == None:
						member.discount = 0
					member.hitCodeNeed += args['auditCharge']
					member.discount += args['auditCharge']

				db.session.add(deposit)
				db.session.add(member)
				db.session.add(user)
				db.session.add(member_account_change_record)
				deposits.append(deposit)

			db.session.commit()
			OperationHistory().PublicDataGo(args['type'], deposits)
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([]), 201


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
			Deposit.query.filter(Deposit.number == orderId).update(args)
			MemberAccountChangeRecord.query.filter(MemberAccountChangeRecord.orderId == orderId,MemberAccountChangeRecord.accountChangeType == 900001).update(args)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return make_response([])
