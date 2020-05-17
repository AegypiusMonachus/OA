from flask import request, g
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
from app.common.orderUtils import *
from app.models import db
from app.models.common.utils import *
from app.models.member import Member
from app.models.member_account_change import MemberAccountChangeRecord, Withdrawal
from app.common.utils import *
from ..common import *
from ..common.utils import *
from app.models.memeber_history import OperationHistory
from flask.json import jsonify
from app.models.user import User

class SystemWithdrawalTypes(Resource):
	def get(self):
		return [
			{'id': 900002, 'name': '后台提存（出款）'},
			{'id': 900007, 'name': '优惠活动'},
			{'id': 900008, 'name': '补发派奖'},
			{'id': 900009, 'name': '返水'},
			{'id': 900010, 'name': '其他'},
		]

class SystemWithdrawals(Resource):

	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('auditUserPassword', type=str, required=True)
		parser.add_argument('username', type=str, required=True)
		parser.add_argument('amount', type=float, required=True)
		parser.add_argument('type', type=int, default=900002)
		parser.add_argument('remarkFront', type=str)
		parser.add_argument('remark', type=str)
		parser.add_argument('isAcdemen', type=int, default=0)
		args = parser.parse_args(strict=True)

		password = args.pop('auditUserPassword')
		user = User.query.get(g.current_user.id)
		if not user or not user.verify_password(password):
			return jsonify({
				'success': False,
				'errorCode': 403,
				'errorMsg': '密码验证失败'
			})
		# if user.withdrawallimitOnce is not None:
		# 	if args['amount'] > user.withdrawallimitOnce:
		# 		return jsonify({
		# 			'success': False,
		# 			'errorCode': 403,
		# 			'errorMsg': '超出单次提款上限'
		# 		})
		# if user.withdrawallimitSumCeiling is not None:
		# 	if user.withdrawallimitSum == None:
		# 		user.withdrawallimitSum = 0
		# 	if args['amount'] > user.withdrawallimitSumCeiling - user.withdrawallimitSum:
		# 		return jsonify({
		# 			'success': False,
		# 			'errorCode': 403,
		# 			'errorMsg': '超出您的总提出限额'
		# 		})
		try:
			withdrawals = []
			members = Member.query.filter(Member.username.in_(args['username'].split(',')),Member.status == 2).all()
			if members:
				datas = []
				for member in members:
					datas.append(member.username)
				return {"success": False, "errorMsg": "批次处理的用户中有已被冻结的用户","data":datas}
			else:
				members = Member.query.filter(Member.username.in_(args['username'].split(','))).all()

			for member in members:
				if member.balance < args['amount']:
					return {"success":False,"errorMsg":"您的余额不足，请重新输入"}

				withdrawal = Withdrawal()
				withdrawal.status = 2
				withdrawal.type = args['type']
				withdrawal.isAcdemen = args['isAcdemen']
				withdrawal.memberId = member.id
				withdrawal.applicationAmount = args['amount']
				withdrawal.applicationTime = time_to_value()
				withdrawal.applicationHost = host_to_value(request.remote_addr)
				withdrawal.withdrawalAmount = withdrawal.applicationAmount
				withdrawal.auditUser = g.current_user.id
				withdrawal.auditTime = time_to_value()
				withdrawal.auditHost = host_to_value(request.remote_addr)
				if args['type'] == 900002:
					withdrawal.info = '后台提存（出款）'
				elif args['type'] == 900007:
					withdrawal.info = '优惠活动（出款）'
				elif args['type'] == 900008:
					withdrawal.info = '补发派奖（出款）'
				elif args['type'] == 900009:
					withdrawal.info = '返水（出款）'
				elif args['type'] == 900010:
					withdrawal.info = '其他（出款）'
				uid = member.id
				withdrawal.orderID = createOrderIdNew(uid=uid)

				member_account_change_record = MemberAccountChangeRecord()
				member_account_change_record.memberId = member.id
				member_account_change_record.memberBalance = member.balance - withdrawal.withdrawalAmount
				member_account_change_record.memberFrozenBalance = member.frozenBalance
				member_account_change_record.amount = -withdrawal.withdrawalAmount
				member_account_change_record.accountChangeType = withdrawal.type
				if args['type'] == 900002:
					member_account_change_record.info = '后台提存（出款）'
				elif args['type'] == 900007:
					member_account_change_record.info = '优惠活动（出款）'
				elif args['type'] == 900008:
					member_account_change_record.info = '补发派奖（出款）'
				elif args['type'] == 900009:
					member_account_change_record.info = '返水（出款）'
				elif args['type'] == 900010:
					member_account_change_record.info = '其他（出款）'
				member_account_change_record.time = withdrawal.auditTime
				member_account_change_record.host = withdrawal.auditHost
				member_account_change_record.actionUID = g.current_user.id
				member_account_change_record.isAcdemen = args['isAcdemen']
				uid = member.id
				member_account_change_record.orderId = withdrawal.orderID
				member_account_change_record.rechargeid = withdrawal.orderID

				member.balance -= args['amount']
				if user.withdrawallimitSum == None:
					user.withdrawallimitSum = 0
				user.withdrawallimitSum += args['amount']

				db.session.add(withdrawal)
				db.session.add(member)
				db.session.add(user)
				db.session.add(member_account_change_record)
				withdrawals.append(withdrawal)
			db.session.commit()
			OperationHistory().PublicDatasAll(args['type'], withdrawals)
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
			Withdrawal.query.filter(Withdrawal.orderID == orderId).update(args)
			MemberAccountChangeRecord.query.filter(MemberAccountChangeRecord.orderId == orderId,MemberAccountChangeRecord.accountChangeType == 900002).update(args)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return make_response([])
