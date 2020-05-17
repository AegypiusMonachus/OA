from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
from sqlalchemy import literal
from app.models import db
from app.models.common.utils import *
from app.models.member_account_change import MemberAccountChangeRecord,Deposit,Withdrawal
from app.models.entertainment_city_bets_detail import EntertainmentCityBetsDetail
from app.models.user import User
from app.models.member import Member
from app.models.member_level import MemberLevel
from app.gateway.gsrkGW import GsrkGW
from app.common.utils import *
from ..common import *
from ..common.utils import *
from sqlalchemy.sql import union,union_all
import sqlalchemy
from sqlalchemy.orm import aliased
from sqlalchemy import func
from sqlalchemy import or_,and_
import os
from openpyxl import Workbook
from app.common.dataUtils import changeData_str

class MemberAccountChangeTypes(Resource):
	d = {
		100001: '会员充值（银行）',
		100002: '会员充值（支付）',
		200001: '会员提现（申请）',
		200002: '会员提现（出款）',
		200003: '会员提现（退回）',
		900001: '后台提存（入款）',
		900002: '后台提存（出款）',
		110001: '其他',
	}
	def get(self):
		return MemberAccountChangeTypes.d

class MemberAccountChangeRecords(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'orderId': fields.String,
		'memberId': fields.Integer,
		'accountChangeType': fields.Integer,
		'accountChangeTypesName': fields.String,
		'time': fields.Integer,
		'eccode': fields.String,
		'rechargeid': fields.String,
		'memberType': fields.String,
		'amount': fields.Float,
		'balanceBefore': fields.Float,
		'balanceAfter': fields.Float,
		'frozenBalanceBefore': fields.Float,
		'frozenBalanceAfter': fields.Float,
		'remark': fields.String,
		'username': fields.String,
		'levelId': fields.Integer,
		'levelName': fields.String,
		'OperatorName': fields.String
	}, totalAmount=fields.Float))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

		parser.add_argument('id', type=str)
		parser.add_argument('accountChangeType', type=str)
		parser.add_argument('isAcdemen', type=int)
		parser.add_argument('timeLower', type=int)
		parser.add_argument('timeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('rechargeid', type=str)
		parser.add_argument('orderId', type=str)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('memberLevelConfig', type=str)
		parser.add_argument('memberParentUsername', type=str)
		args = parser.parse_args(strict=True)
		args['accountChangeType'] = args['accountChangeType'].split(',')
		criterion = set()
		criterion.add(Member.isTsetPLay != 1)
		if args['id']:
			criterion.add(MemberAccountChangeRecord.id.in_(args['id'].split(',')))

		if args['isAcdemen'] is not None:
			if args['isAcdemen'] == 1:
				criterion.add(MemberAccountChangeRecord.isAcdemen == args['isAcdemen'])
				if '6' in args['accountChangeType']:
					args['accountChangeType'].remove('6')
			else:
				criterion.add(or_(MemberAccountChangeRecord.isAcdemen.is_(None),MemberAccountChangeRecord.isAcdemen == 0))
		if args['rechargeid']:
			criterion.add(MemberAccountChangeRecord.rechargeid == args['rechargeid'])
		if args['accountChangeType']:
			criterion.add(MemberAccountChangeRecord.accountChangeType.in_(args['accountChangeType']))
		if args['timeLower']:
			criterion.add(MemberAccountChangeRecord.time >= args['timeLower'])
		if args['timeUpper']:
			criterion.add(MemberAccountChangeRecord.time <= args['timeUpper'] + SECONDS_PER_DAY)
		# if args['amountUpper']:
		# 	criterion.add(MemberAccountChangeRecord.amount <= args['amountUpper'])
		# if args['amountLower']:
		# 	criterion.add(MemberAccountChangeRecord.amount <= args['amountLower'])
		if args['amountUpper'] is not None and args['amountLower'] is not None:
			if args['amountUpper'] >= args['amountLower']:
				criterion.add(MemberAccountChangeRecord.amount <= args['amountUpper'])
				criterion.add(MemberAccountChangeRecord.amount >= args['amountLower'])
			else:
				criterion.add(MemberAccountChangeRecord.amount >= args['amountUpper'])
				criterion.add(MemberAccountChangeRecord.amount <= args['amountLower'])
		elif args['amountUpper'] is not None:
			if args['amountUpper'] >= 0:
				criterion.add(MemberAccountChangeRecord.amount <= args['amountUpper'])
			else:
				criterion.add(MemberAccountChangeRecord.amount >= args['amountUpper'])
		elif args['amountLower'] is not None:
			if args['amountLower'] >= 0:
				criterion.add(MemberAccountChangeRecord.amount >= args['amountLower'])
			else:
				criterion.add(MemberAccountChangeRecord.amount <= args['amountLower'])

		if args['orderId']:
			criterion.add(MemberAccountChangeRecord.orderId == args['orderId'])
		if args['memberUsername']:
			criterion.add(Member.username.in_(args['memberUsername'].split(',')))
		if args['memberLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))
# 		if args['memberLevelConfig'] is None:
# 			criterion.add(Member.levelConfig == '')
		if args['memberParentUsername']:
			parent = Member.query.filter(Member.username == args['memberParentUsername']).first()
			if parent:
				criterion.add(Member.parent == parent.id)
		query = db.session.query(
			MemberAccountChangeRecord.id.label('id'),
			MemberAccountChangeRecord.orderId.label('orderId'),
			MemberAccountChangeRecord.time.label('time'),
			MemberAccountChangeRecord.accountChangeType.label('accountChangeType'),
			MemberAccountChangeRecord.info.label('accountChangeTypesName'),
			MemberAccountChangeRecord.amount.label('amount'),
			MemberAccountChangeRecord.rechargeid.label('rechargeid'),
			MemberAccountChangeRecord.memberBalance.label('balanceAfter'),
			literal(0).label('balanceBefore'),
			MemberAccountChangeRecord.memberFrozenBalance.label('frozenBalanceBefore'),
			literal('KK').label('eccode'),
			Member.id.label('memberId'),
			Member.username.label('username'),
			Member.type.label('memberType'),
			MemberLevel.levelName.label('levelName'),
			MemberLevel.id.label('levelId'),
			User.username.label('OperatorName')
		).order_by(MemberAccountChangeRecord.time.desc())

		query = query.outerjoin(Member, MemberAccountChangeRecord.memberId == Member.id)
		query = query.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
		query = query.outerjoin(User, User.id == MemberAccountChangeRecord.actionUID)
		result_query = []
		if args['accountChangeType']:
			if '6' in args['accountChangeType']:
				query_yule = db.session.query(
					EntertainmentCityBetsDetail.id.label('id'),
					EntertainmentCityBetsDetail.BillNo.label('orderId'),
					EntertainmentCityBetsDetail.BetTime.label('time'),
					literal(6).label('accountChangeType'),
					EntertainmentCityBetsDetail.Remark.label('accountChangeTypesName'),
					EntertainmentCityBetsDetail.Profit.label('amount'),
					EntertainmentCityBetsDetail.BillNo.label('rechargeid'),
					EntertainmentCityBetsDetail.Balance.label('balanceAfter'),
					literal(0).label('balanceBefore'),
					EntertainmentCityBetsDetail.CusAccount.label('frozenBalanceBefore'),
					EntertainmentCityBetsDetail.ECCode.label('eccode'),
					Member.id.label('memberId'),
					Member.username.label('username'),
					Member.type.label('memberType'),
					MemberLevel.levelName.label('levelName'),
					MemberLevel.id.label('levelId'),
					literal('').label('OperatorName')
				).order_by(EntertainmentCityBetsDetail.BetTime.desc())
				query_yule = query_yule.outerjoin(Member, EntertainmentCityBetsDetail.PlayerName == Member.username)
				query_yule = query_yule.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
				criterion_query = set()
				if args['id']:
					criterion_query.add(EntertainmentCityBetsDetail.id.in_(args['id'].split(',')))
				if args['rechargeid']:
					criterion_query.add(EntertainmentCityBetsDetail.BillNo == args['rechargeid'])
				if args['timeLower']:
					criterion_query.add(EntertainmentCityBetsDetail.BetTime >= args['timeLower'])
				if args['timeUpper']:
					criterion_query.add(EntertainmentCityBetsDetail.BetTime <= args['timeUpper'] + SECONDS_PER_DAY)
				# if args['amountLower']:
				# 	criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountLower'])
				# if args['amountUpper']:
				# 	criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountUpper'])
				if args['amountUpper'] is not None and args['amountLower'] is not None:
					if args['amountUpper'] >= args['amountLower']:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountUpper'])
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountLower'])
					else:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountUpper'])
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountLower'])
				elif args['amountUpper'] is not None:
					if args['amountUpper'] >= 0:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountUpper'])
					else:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountUpper'])
				elif args['amountLower'] is not None:
					if args['amountLower'] >= 0:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountLower'])
					else:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountLower'])

				if args['orderId']:
					criterion_query.add(EntertainmentCityBetsDetail.BillNo == args['orderId'])
				if args['memberUsername']:
					criterion_query.add(Member.username.in_(args['memberUsername'].split(',')))
				if args['memberLevelConfig']:
					criterion_query.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))
# 				if args['memberLevelConfig'] is None:
# 					criterion_query.add(Member.levelConfig == '')
				if args['memberParentUsername']:
					parent = Member.query.filter(Member.username == args['memberParentUsername']).first()
					if parent:
						criterion_query.add(Member.parent == parent.id)
				query = query.filter(*criterion)
				query_yule = query_yule.filter(*criterion_query)
				# union_all 拼接数据
				result = union_all(query,query_yule)

				# 将拼接好的数据重新命名，变成一个新的查询表
				user_alias = aliased(result, name='user_alias')
				user_alias = db.session.query(user_alias).order_by(user_alias.c.time.desc())

				pagination = paginate_one(user_alias,args['page'], args['pageSize'])
				pagination = convert_pagination(pagination)

				total_amount = 0
				for item in pagination.items:
					total_amount += item['amount']
					item['accountChangeTypeName'] = MemberAccountChangeTypes.d.get(item['accountChangeType'])

# 					if item['accountChangeType'] in [100001, 100002]:
# 						item['balanceAfter'] = item['balanceBefore'] + item['amount']
# 						item['frozenBalanceAfter'] = item['frozenBalanceBefore']
# 
# 					if item['accountChangeType'] in [200001]:
# 						item['balanceAfter'] = item['balanceBefore'] - item['amount']
# 						item['frozenBalanceAfter'] = item['frozenBalanceBefore'] + item['amount']
# 
# 					if item['accountChangeType'] in [200002]:
# 						item['balanceAfter'] = item['balanceBefore']
# 						item['frozenBalanceAfter'] = item['frozenBalanceBefore'] - item['amount']
# 
# 					if item['accountChangeType'] in [200003]:
# 						item['balanceAfter'] = item['balanceBefore'] + item['amount']
# 						item['frozenBalanceAfter'] = item['frozenBalanceBefore'] - item['amount']
# 
# 					if item['accountChangeType'] in [900001]:
# 						item['balanceAfter'] = item['balanceBefore'] + item['amount']
# 						item['frozenBalanceAfter'] = item['frozenBalanceBefore']
# 
# 					if item['accountChangeType'] in [900002]:
# 						item['balanceAfter'] = item['balanceBefore'] - item['amount']
# 						item['frozenBalanceAfter'] = item['frozenBalanceBefore']
				return make_response_from_pagination(pagination, totalAmount=total_amount)
		pagination = paginate(query, criterion, args['page'], args['pageSize'])
		pagination = convert_pagination(pagination)
		total_amount = 0
		for item in pagination.items:
			total_amount += item['amount']
# 			item['accountChangeTypeName'] = MemberAccountChangeTypes.d.get(item['accountChangeType'])
# 
# 			if item['accountChangeType'] in [100001, 100002]:
# 				item['balanceAfter'] = item['balanceBefore'] + item['amount']
# 				item['frozenBalanceAfter'] = item['frozenBalanceBefore']
# 
# 			if item['accountChangeType'] in [200001]:
# 				item['balanceAfter'] = item['balanceBefore'] - item['amount']
# 				item['frozenBalanceAfter'] = item['frozenBalanceBefore'] + item['amount']
# 
# 			if item['accountChangeType'] in [200002]:
# 				item['balanceAfter'] = item['balanceBefore']
# 				item['frozenBalanceAfter'] = item['frozenBalanceBefore'] - item['amount']
# 
# 			if item['accountChangeType'] in [200003]:
# 				item['balanceAfter'] = item['balanceBefore'] + item['amount']
# 				item['frozenBalanceAfter'] = item['frozenBalanceBefore'] - item['amount']
# 
# 			if item['accountChangeType'] in [900001]:
# 				item['balanceAfter'] = item['balanceBefore'] + item['amount']
# 				item['frozenBalanceAfter'] = item['frozenBalanceBefore']
# 
# 			if item['accountChangeType'] in [900002]:
# 				item['balanceAfter'] = item['balanceBefore'] - item['amount']
# 				item['frozenBalanceAfter'] = item['frozenBalanceBefore']
		return make_response_from_pagination(pagination, totalAmount=total_amount)

	# def put(self,id):
	# 	parser = RequestParser(trim=True)
	# 	parser.add_argument('state', type=int)
	# 	args = parser.parse_args(strict=True)
	# 	recharge = Deposit.query.get(id)
	# 	if recharge.status != 1:
	# 		return make_response(data=[],error_code=1010, error_message="申请状态错误")
	# 	if args['state'] == 99 or args['state'] == 3:
	# 		for key, value in args.items():
	# 			setattr(recharge, 'status', args['state'])
	# 		try:
	# 			db.session.add(recharge)
	# 			db.session.commit()
	# 		except:
	# 			db.session.rollback()
	# 			db.session.remove()
	# 			abort(500)
	# 		return make_response([])
	# 	elif args['state'] == 2:
	# 		gsrkgw = GsrkGW()
	# 		gsrkgw.amount = recharge.applicationAmount
	# 		gsrkgw.oderid = recharge.number
	# 		gsrkgw.accountChange(100003)
	# 	return make_response([]), 201

class ExportMemberAccountChangeRecords(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

		parser.add_argument('id', type=str)
		parser.add_argument('accountChangeType', type=str)
		parser.add_argument('isAcdemen', type=int)
		parser.add_argument('timeLower', type=int)
		parser.add_argument('timeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('rechargeid', type=str)
		parser.add_argument('orderId', type=str)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('memberLevelConfig', type=str)
		parser.add_argument('memberParentUsername', type=str)
		args = parser.parse_args(strict=True)
		args['accountChangeType'] = args['accountChangeType'].split(',')
		criterion = set()
		criterion.add(Member.isTsetPLay != 1)
		if args['id']:
			criterion.add(MemberAccountChangeRecord.id.in_(args['id'].split(',')))

		if args['isAcdemen'] is not None:
			if args['isAcdemen'] == 1:
				criterion.add(MemberAccountChangeRecord.isAcdemen == args['isAcdemen'])
				if '6' in args['accountChangeType']:
					args['accountChangeType'].remove('6')
			else:
				criterion.add(
					or_(MemberAccountChangeRecord.isAcdemen.is_(None), MemberAccountChangeRecord.isAcdemen == 0))
		if args['rechargeid']:
			criterion.add(MemberAccountChangeRecord.rechargeid == args['rechargeid'])
		if args['accountChangeType']:
			criterion.add(MemberAccountChangeRecord.accountChangeType.in_(args['accountChangeType']))
		if args['timeLower']:
			criterion.add(MemberAccountChangeRecord.time >= args['timeLower'])
		if args['timeUpper']:
			criterion.add(MemberAccountChangeRecord.time <= args['timeUpper'] + SECONDS_PER_DAY)
		# if args['amountUpper']:
		# 	criterion.add(MemberAccountChangeRecord.amount <= args['amountUpper'])
		# if args['amountLower']:
		# 	criterion.add(MemberAccountChangeRecord.amount <= args['amountLower'])
		if args['amountUpper'] is not None and args['amountLower'] is not None:
			if args['amountUpper'] >= args['amountLower']:
				criterion.add(MemberAccountChangeRecord.amount <= args['amountUpper'])
				criterion.add(MemberAccountChangeRecord.amount >= args['amountLower'])
			else:
				criterion.add(MemberAccountChangeRecord.amount >= args['amountUpper'])
				criterion.add(MemberAccountChangeRecord.amount <= args['amountLower'])
		elif args['amountUpper'] is not None:
			if args['amountUpper'] >= 0:
				criterion.add(MemberAccountChangeRecord.amount <= args['amountUpper'])
			else:
				criterion.add(MemberAccountChangeRecord.amount >= args['amountUpper'])
		elif args['amountLower'] is not None:
			if args['amountLower'] >= 0:
				criterion.add(MemberAccountChangeRecord.amount >= args['amountLower'])
			else:
				criterion.add(MemberAccountChangeRecord.amount <= args['amountLower'])

		if args['orderId']:
			criterion.add(MemberAccountChangeRecord.orderId == args['orderId'])
		if args['memberUsername']:
			criterion.add(Member.username.in_(args['memberUsername'].split(',')))
		if args['memberLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))
		# 		if args['memberLevelConfig'] is None:
		# 			criterion.add(Member.levelConfig == '')
		if args['memberParentUsername']:
			parent = Member.query.filter(Member.username == args['memberParentUsername']).first()
			if parent:
				criterion.add(Member.parent == parent.id)
		query = db.session.query(
			MemberAccountChangeRecord.orderId.label('orderId'),
			Member.username.label('username'),
			MemberLevel.levelName.label('levelName'),
			MemberAccountChangeRecord.time.label('time'),
			MemberAccountChangeRecord.info.label('accountChangeTypesName'),
			MemberAccountChangeRecord.amount.label('amount'),
			MemberAccountChangeRecord.memberBalance.label('memberBalance'),
			User.username.label('OperatorName'),
			User.username.label('dealName'),
		).order_by(MemberAccountChangeRecord.time.desc())
		query = query.outerjoin(Member, MemberAccountChangeRecord.memberId == Member.id)
		query = query.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
		query = query.outerjoin(User, User.id == MemberAccountChangeRecord.actionUID)
		result_query = []
		if args['accountChangeType']:
			if '6' in args['accountChangeType']:
				query_yule = db.session.query(
					EntertainmentCityBetsDetail.BillNo.label('orderId'),
					Member.username.label('username'),
					MemberLevel.levelName.label('levelName'),
					EntertainmentCityBetsDetail.BetTime.label('time'),
					func.concat(EntertainmentCityBetsDetail.ECCode, '-派彩').label('accountChangeTypesName'),
					EntertainmentCityBetsDetail.Profit.label('amount'),
					EntertainmentCityBetsDetail.Balance.label('memberBalance'),
					literal('').label('OperatorName'),
					literal('').label('dealName'),
				).order_by(EntertainmentCityBetsDetail.BetTime.desc())
				query_yule = query_yule.outerjoin(Member, EntertainmentCityBetsDetail.PlayerName == Member.username)
				query_yule = query_yule.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
				criterion_query = set()
				if args['id']:
					criterion_query.add(EntertainmentCityBetsDetail.id.in_(args['id'].split(',')))
				if args['rechargeid']:
					criterion_query.add(EntertainmentCityBetsDetail.BillNo == args['rechargeid'])
				if args['timeLower']:
					criterion_query.add(EntertainmentCityBetsDetail.BetTime >= args['timeLower'])
				if args['timeUpper']:
					criterion_query.add(EntertainmentCityBetsDetail.BetTime <= args['timeUpper'] + SECONDS_PER_DAY)
				# if args['amountLower']:
				# 	criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountLower'])
				# if args['amountUpper']:
				# 	criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountUpper'])
				if args['amountUpper'] is not None and args['amountLower'] is not None:
					if args['amountUpper'] >= args['amountLower']:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountUpper'])
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountLower'])
					else:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountUpper'])
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountLower'])
				elif args['amountUpper'] is not None:
					if args['amountUpper'] >= 0:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountUpper'])
					else:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountUpper'])
				elif args['amountLower'] is not None:
					if args['amountLower'] >= 0:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountLower'])
					else:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountLower'])

				if args['orderId']:
					criterion_query.add(EntertainmentCityBetsDetail.BillNo == args['orderId'])
				if args['memberUsername']:
					criterion_query.add(Member.username.in_(args['memberUsername'].split(',')))
				if args['memberLevelConfig']:
					criterion_query.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))
				# 				if args['memberLevelConfig'] is None:
				# 					criterion_query.add(Member.levelConfig == '')
				if args['memberParentUsername']:
					parent = Member.query.filter(Member.username == args['memberParentUsername']).first()
					if parent:
						criterion_query.add(Member.parent == parent.id)
				query = query.filter(*criterion)
				query_yule = query_yule.filter(*criterion_query)
				# union_all 拼接数据
				result = union_all(query, query_yule)

				# 将拼接好的数据重新命名，变成一个新的查询表
				user_alias = aliased(result, name='user_alias')
				user_alias = db.session.query(user_alias).order_by(user_alias.c.time.desc()).all()
				results = []
				for item in user_alias:
					results.append(
						(item[0],
						item[1],
						item[2],
						changeData_str(item[3]),
						item[4],
						item[5],
						item[6],
						item[7],
						item[8])
					)
				title = ['单号', '帐号', '会员等级', '操作时间', '信息', '金额', '小计', '操作人员',
						 '处理人员', '其他']
				workbook = Workbook()
				worksheet = workbook.active

				worksheet.append(title)
				worksheet.column_dimensions['A'].width = 20
				worksheet.column_dimensions['B'].width = 10
				worksheet.column_dimensions['C'].width = 18
				worksheet.column_dimensions['D'].width = 20
				worksheet.column_dimensions['E'].width = 15
				worksheet.column_dimensions['F'].width = 8
				worksheet.column_dimensions['G'].width = 8
				worksheet.column_dimensions['H'].width = 8
				worksheet.column_dimensions['I'].width = 8
				worksheet.column_dimensions['J'].width = 8
				for result in results:
					worksheet.append(result)
				filename = '交易记录-' + str(int(time.time())) + '.xlsx'
				workbook.save(os.path.join(current_app.static_folder, filename))
				return make_response([{
					'success': True,
					'resultFilename': filename,
				}])

		query = query.filter(*criterion).all()
		results = []
		for item in query:
			results.append(
				(item[0],
				 item[1],
				 item[2],
				 changeData_str(item[3]),
				 item[4],
				 item[5],
				 item[6],
				 item[7],
				 item[8])
			)
		title = ['单号', '帐号', '会员等级', '操作时间', '信息', '金额', '小计', '操作人员',
				 '处理人员', '其他']
		workbook = Workbook()
		worksheet = workbook.active

		worksheet.append(title)
		worksheet.column_dimensions['A'].width = 20
		worksheet.column_dimensions['B'].width = 10
		worksheet.column_dimensions['C'].width = 18
		worksheet.column_dimensions['D'].width = 20
		worksheet.column_dimensions['E'].width = 15
		worksheet.column_dimensions['F'].width = 8
		worksheet.column_dimensions['G'].width = 8
		worksheet.column_dimensions['H'].width = 8
		worksheet.column_dimensions['I'].width = 8
		worksheet.column_dimensions['J'].width = 8
		for result in results:
			worksheet.append(result)
		filename = '交易记录-' + str(int(time.time())) + '.xlsx'
		workbook.save(os.path.join(current_app.static_folder, filename))
		return make_response([{
			'success': True,
			'resultFilename': filename,
		}])


class GetMemberAccountChangeRecords(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

		parser.add_argument('id', type=str)
		parser.add_argument('accountChangeType', type=str)
		parser.add_argument('timeLower', type=int)
		parser.add_argument('timeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('rechargeid', type=int)
		parser.add_argument('orderId', type=int)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('memberLevelConfig', type=str)
		parser.add_argument('memberParentUsername', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		if args['id']:
			criterion.add(MemberAccountChangeRecord.id.in_(args['id'].split(',')))
		if args['rechargeid']:
			criterion.add(MemberAccountChangeRecord.rechargeid == args['rechargeid'])
		if args['accountChangeType']:
			criterion.add(MemberAccountChangeRecord.accountChangeType.in_(args['accountChangeType'].split(',')))
		if args['timeLower']:
			criterion.add(MemberAccountChangeRecord.time >= args['timeLower'])
		if args['timeUpper']:
			criterion.add(MemberAccountChangeRecord.time <= args['timeUpper'] + SECONDS_PER_DAY)
		if args['amountLower']:
			criterion.add(MemberAccountChangeRecord.amount >= args['amountLower'])
		if args['amountUpper']:
			criterion.add(MemberAccountChangeRecord.amount <= args['amountUpper'])
		if args['orderId']:
			criterion.add(MemberAccountChangeRecord.orderId == args['orderId'])

		# member_criterion = set()
		if args['memberUsername']:
			criterion.add(Member.username.in_(args['memberUsername'].split(',')))
		if args['memberLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))
		if args['memberParentUsername']:
			parent = Member.query.filter(Member.username == args['memberParentUsername']).first()
			if parent:
				criterion.add(Member.parent == parent.id)

		# subquery = db.session.query(
		#
		# ).join(MemberLevel, Member.levelConfig == MemberLevel.id).filter(*member_criterion).subquery()

		query = db.session.query(
			MemberAccountChangeRecord.id,
			MemberAccountChangeRecord.memberId,
			MemberAccountChangeRecord.orderId,
			MemberAccountChangeRecord.time,
			MemberAccountChangeRecord.accountChangeType,
			MemberAccountChangeRecord.amount,
			MemberAccountChangeRecord.rechargeid,
			MemberAccountChangeRecord.memberBalance.label('balanceBefore'),
			MemberAccountChangeRecord.memberFrozenBalance.label('frozenBalanceBefore'),
			Member.id.label('memberId'),
			Member.username,
			MemberLevel.levelName,
			MemberLevel.id.label('levelId'),
			User.username.label('UsersName')
		)

		query = query.outerjoin(Member, MemberAccountChangeRecord.memberId == Member.id)
		query = query.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
		query = query.outerjoin(User, User.id == MemberAccountChangeRecord.actionUID)
		pagination = paginate(query, criterion, args['page'], args['pageSize'])
		pagination = convert_pagination(pagination)

		total_amount = 0
		for item in pagination.items:
			total_amount += item['amount']
			item['accountChangeTypeName'] = MemberAccountChangeTypes.d.get(item['accountChangeType'])

			if item['accountChangeType'] in [100001, 100002]:
				item['balanceAfter'] = item['balanceBefore'] + item['amount']
				item['frozenBalanceAfter'] = item['frozenBalanceBefore']

			if item['accountChangeType'] in [200001]:
				item['balanceAfter'] = item['balanceBefore'] - item['amount']
				item['frozenBalanceAfter'] = item['frozenBalanceBefore'] + item['amount']

			if item['accountChangeType'] in [200002]:
				item['balanceAfter'] = item['balanceBefore']
				item['frozenBalanceAfter'] = item['frozenBalanceBefore'] - item['amount']

			if item['accountChangeType'] in [200003]:
				item['balanceAfter'] = item['balanceBefore'] + item['amount']
				item['frozenBalanceAfter'] = item['frozenBalanceBefore'] - item['amount']

			if item['accountChangeType'] in [900001]:
				item['balanceAfter'] = item['balanceBefore'] + item['amount']
				item['frozenBalanceAfter'] = item['frozenBalanceBefore']

			if item['accountChangeType'] in [900002]:
				item['balanceAfter'] = item['balanceBefore'] - item['amount']
				item['frozenBalanceAfter'] = item['frozenBalanceBefore']

		return make_response_from_pagination(pagination, totalAmount=total_amount)

class GetMemberAccountMoney(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

		parser.add_argument('id', type=str)
		parser.add_argument('accountChangeType', type=str)
		parser.add_argument('isAcdemen', type=int)
		parser.add_argument('timeLower', type=int)
		parser.add_argument('timeUpper', type=int)
		parser.add_argument('amountLower', type=float)
		parser.add_argument('amountUpper', type=float)
		parser.add_argument('rechargeid', type=str)
		parser.add_argument('orderId', type=str)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('memberLevelConfig', type=str)
		parser.add_argument('memberParentUsername', type=str)
		args = parser.parse_args(strict=True)
		args['accountChangeType'] = args['accountChangeType'].split(',')
		criterion = set()
		criterion.add(Member.isTsetPLay != 1)
		if args['id']:
			criterion.add(MemberAccountChangeRecord.id.in_(args['id'].split(',')))

		if args['isAcdemen'] is not None:
			if args['isAcdemen'] == 1:
				criterion.add(MemberAccountChangeRecord.isAcdemen == args['isAcdemen'])
				if '6' in args['accountChangeType']:
					args['accountChangeType'].remove('6')
			else:
				criterion.add(or_(MemberAccountChangeRecord.isAcdemen.is_(None), MemberAccountChangeRecord.isAcdemen == 0))
		if args['rechargeid']:
			criterion.add(MemberAccountChangeRecord.rechargeid == args['rechargeid'])
		if args['accountChangeType']:
			criterion.add(MemberAccountChangeRecord.accountChangeType.in_(args['accountChangeType']))
		if args['timeLower']:
			criterion.add(MemberAccountChangeRecord.time >= args['timeLower'])
		if args['timeUpper']:
			criterion.add(MemberAccountChangeRecord.time <= args['timeUpper'] + SECONDS_PER_DAY)
		# if args['amountUpper']:
		# 	criterion.add(MemberAccountChangeRecord.amount <= args['amountUpper'])
		# if args['amountLower']:
		# 	criterion.add(MemberAccountChangeRecord.amount <= args['amountLower'])
		if args['amountUpper'] is not None and args['amountLower'] is not None:
			if args['amountUpper'] >= args['amountLower']:
				criterion.add(MemberAccountChangeRecord.amount <= args['amountUpper'])
				criterion.add(MemberAccountChangeRecord.amount >= args['amountLower'])
			else:
				criterion.add(MemberAccountChangeRecord.amount >= args['amountUpper'])
				criterion.add(MemberAccountChangeRecord.amount <= args['amountLower'])
		elif args['amountUpper'] is not None:
			if args['amountUpper'] >= 0:
				criterion.add(MemberAccountChangeRecord.amount <= args['amountUpper'])
			else:
				criterion.add(MemberAccountChangeRecord.amount >= args['amountUpper'])
		elif args['amountLower'] is not None:
			if args['amountLower'] >= 0:
				criterion.add(MemberAccountChangeRecord.amount >= args['amountLower'])
			else:
				criterion.add(MemberAccountChangeRecord.amount <= args['amountLower'])

		if args['orderId']:
			criterion.add(MemberAccountChangeRecord.orderId == args['orderId'])
		if args['memberUsername']:
			criterion.add(Member.username.in_(args['memberUsername'].split(',')))
		if args['memberLevelConfig']:
			criterion.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))
		# 		if args['memberLevelConfig'] is None:
		# 			criterion.add(Member.levelConfig == '')
		if args['memberParentUsername']:
			parent = Member.query.filter(Member.username == args['memberParentUsername']).first()
			if parent:
				criterion.add(Member.parent == parent.id)
		query = db.session.query(
			func.sum(MemberAccountChangeRecord.amount).label('sumAmount')
		)

		query = query.outerjoin(Member, MemberAccountChangeRecord.memberId == Member.id)
		query = query.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
		query = query.outerjoin(User, User.id == MemberAccountChangeRecord.actionUID)
		result_query = []
		if args['accountChangeType']:
			if '6' in args['accountChangeType']:
				query_yule = db.session.query(
					func.sum(EntertainmentCityBetsDetail.Profit).label('sumAmount')
				)
				query_yule = query_yule.outerjoin(Member, EntertainmentCityBetsDetail.PlayerName == Member.username)
				query_yule = query_yule.outerjoin(MemberLevel, Member.levelConfig == MemberLevel.id)
				criterion_query = set()
				if args['id']:
					criterion_query.add(EntertainmentCityBetsDetail.id.in_(args['id'].split(',')))
				if args['rechargeid']:
					criterion_query.add(EntertainmentCityBetsDetail.BillNo == args['rechargeid'])
				if args['timeLower']:
					criterion_query.add(EntertainmentCityBetsDetail.BetTime >= args['timeLower'])
				if args['timeUpper']:
					criterion_query.add(EntertainmentCityBetsDetail.BetTime <= args['timeUpper'] + SECONDS_PER_DAY)
				# if args['amountLower']:
				# 	criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountLower'])
				# if args['amountUpper']:
				# 	criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountUpper'])
				if args['amountUpper'] is not None and args['amountLower'] is not None:
					if args['amountUpper'] >= args['amountLower']:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountUpper'])
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountLower'])
					else:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountUpper'])
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountLower'])
				elif args['amountUpper'] is not None:
					if args['amountUpper'] >= 0:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountUpper'])
					else:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountUpper'])
				elif args['amountLower'] is not None:
					if args['amountLower'] >= 0:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount >= args['amountLower'])
					else:
						criterion_query.add(EntertainmentCityBetsDetail.ValidBetAmount <= args['amountLower'])

				if args['orderId']:
					criterion_query.add(EntertainmentCityBetsDetail.BillNo == args['orderId'])
				if args['memberUsername']:
					criterion_query.add(Member.username.in_(args['memberUsername'].split(',')))
				if args['memberLevelConfig']:
					criterion_query.add(Member.levelConfig.in_(args['memberLevelConfig'].split(',')))
				# 				if args['memberLevelConfig'] is None:
				# 					criterion_query.add(Member.levelConfig == '')
				if args['memberParentUsername']:
					parent = Member.query.filter(Member.username == args['memberParentUsername']).first()
					if parent:
						criterion_query.add(Member.parent == parent.id)
				query = query.filter(*criterion)
				query_yule = query_yule.filter(*criterion_query)
				# union_all 拼接数据
				result = union_all(query, query_yule)


				# 将拼接好的数据重新命名，变成一个新的查询表
				user_alias = aliased(result, name='user_alias')
				user_alias = db.session.query(func.sum(user_alias.c.sumAmount)).all()[0][0]
				return {'success':True,'data':user_alias}
		user_alias = query.filter(*criterion).all()[0][0]
		return {'success': True, 'data': user_alias}

class GetMemberAccountChangeRecordsAl(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('type', type=int)
		parser.add_argument('orderId', type=str)
		args = parser.parse_args(strict=True)
		if args['type'] is not None:
			if args['type'] == 100001:
				isAcde = db.session.query(Deposit.isAcdemen).filter(Deposit.number == args['orderId']).first()
				if isAcde is not None:
					isAcde = isAcde[0]
				isAcdemen = {}
				isAcdemen['isAcdemen'] = isAcde
				return isAcdemen
			if args['type'] == 100002:
				isAcde = db.session.query(Deposit.isAcdemen).filter(Deposit.number == args['orderId']).first()
				if isAcde is not None:
					isAcde = isAcde[0]
				isAcdemen = {}
				isAcdemen['isAcdemen'] = isAcde
				return isAcdemen
			if args['type'] == 200002:
				isAcde = db.session.query(Withdrawal.isAcdemen).filter(Withdrawal.orderID == args['orderId']).first()
				if isAcde is not None:
					isAcde = isAcde[0]
				isAcdemen = {}
				isAcdemen['isAcdemen'] = isAcde
				return isAcdemen
			if args['type'] == 900001:
				isAcde = db.session.query(Deposit.isAcdemen).filter(Deposit.number == args['orderId']).first()
				if isAcde is not None:
					isAcde = isAcde[0]
				isAcdemen = {}
				isAcdemen['isAcdemen'] = isAcde
				return isAcdemen
			if args['type'] == 900002:
				isAcde = db.session.query(Withdrawal.isAcdemen).filter(Withdrawal.orderID == args['orderId']).first()
				if isAcde is not None:
					isAcde = isAcde[0]
				isAcdemen = {}
				isAcdemen['isAcdemen'] = isAcde
				return isAcdemen

		else:
			return {"success": False, "errorMsg": "交易类型不能为空"}
