from flask import g
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
from sqlalchemy import func
import re
from app.models.memeber_history import OperationHistory

from app.models import db
from app.models.common.utils import *
from app.models.member import Member
from app.models.bank_account import (
	Bank,
	SystemBankAccount,
	MemberBankAccount,
	MemberBankAccountModificationLog
)
from app.common.utils import *
from ..common import *
from ..common.utils import *

class Banks(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'name': fields.String,
		'home': fields.String,
		'logo': fields.String,
	}))
	def get(self):
		return make_response_from_pagination(paginate(Bank.query))

	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('name', type=str, required=True)
		parser.add_argument('home', type=str)
		parser.add_argument('logo', type=str)
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value is not None}

		bank = Bank(**args)
		try:
			db.session.add(bank)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([]), 201

	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('name', type=str)
		parser.add_argument('home', type=str)
		parser.add_argument('logo', type=str)
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value is not None}

		bank = Bank.query.get(id)
		for key, value in args.items():
			setattr(bank, key, value)
		try:
			db.session.add(bank)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])

class SystemBankAccountTypes(Resource):
	def get(self):
		return {
			2001: '一般账户',
			2002: '微信支付',
			2003: '支付宝',
			2004: '财付通',
			2005: 'QQ扫码',
			2006: '京东',
			2007: '银联',
			2008: '百度',
		}

class SystemBankAccounts(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'status': fields.Integer,
		'type': fields.Integer,
		'bankName': fields.String,
		'bankId': fields.String,
		'accountNumber': fields.String,
		'accountName': fields.String,
		'subbranchName': fields.String,
		'remark': fields.String,
		'accumulatedAmount': fields.Float,
		'validTime': fields.String,
		'levels': fields.String,
		'amount':fields.Float,
		'url':fields.String
	}))
	def get(self, id=None):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('levels', type=int)
		parser.add_argument('status', type=int)
		parser.add_argument('type', type=int)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
		args = parser.parse_args(strict=True)
		pagination = None
		criterion = set()
		if id is not None:
			criterion.add(SystemBankAccount.id == id)
			criterion.add(SystemBankAccount.isDelete == 0)
		# pagination = paginate(SystemBankAccount.query.filter(SystemBankAccount.id == id ,SystemBankAccount.isDelete == 0), page=args['page'], per_page=args['pageSize'])
		else:
			if args['status'] == 1 or args['status'] == 0:
				criterion.add(SystemBankAccount.status == args['status'])
				criterion.add(SystemBankAccount.isDelete == 0)
			# pagination = paginate(SystemBankAccount.query.filter(SystemBankAccount.status == args['status'],SystemBankAccount.isDelete == 0), page=args['page'], per_page=args['pageSize'])
			elif args['levels']:
				criterion.add(
					func.find_in_set(args['levels'], SystemBankAccount.levels, SystemBankAccount.isDelete == 0))
			# criterion.add(func.find_in_set(args['levels']))
			# criterion.add(SystemBankAccount.isDelete == 0)
			# pagination = paginate(SystemBankAccount.query.filter(func.find_in_set(args['levels'], SystemBankAccount.levels,SystemBankAccount.isDelete == 0)))
			else:
				criterion.add(SystemBankAccount.isDelete == 0)
			# pagination = paginate(SystemBankAccount.query.filter(SystemBankAccount.isDelete == 0), page=args['page'], per_page=args['pageSize'])
			if args['type'] is not None:
				criterion.add(SystemBankAccount.type == args['type'])
		# pagination = paginate(SystemBankAccount.query.filter(SystemBankAccount.type == args['type']), page=args['page'], per_page=args['pageSize'])

		pagination = paginate(SystemBankAccount.query.filter(*criterion), page=args['page'], per_page=args['pageSize'])
		return make_response_from_pagination(pagination)

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'status': fields.Integer,
		'type': fields.Integer,
		'bankName': fields.String,
		'bankId': fields.String,
		'accountNumber': fields.String,
		'accountName': fields.String,
		'subbranchName': fields.String,
		'remark': fields.String,
		'accumulatedAmount': fields.Float,
		'amount': fields.Float,
		'validTime': fields.String,
		'levels': fields.String,
		'url':fields.String
	}))
	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('bankId', type=int, location=['json','args'])
		parser.add_argument('bankName', type=str, location=['json','args'])
		parser.add_argument('type', type=int, location=['json','args'])
		parser.add_argument('accountNumber', type=str, location=['json','args'])
		parser.add_argument('accountName', type=str, location=['json','args'])
		parser.add_argument('subbranchName', type=str, location=['json','args'])
		parser.add_argument('remark', type=str, location=['json','args'])
		parser.add_argument('validTime', type=int, location=['json','args'])
		parser.add_argument('levels', type=str, location=['json','args'])
		parser.add_argument('url', type=str, location=['json','args'])
		args = parser.parse_args(strict=True)
		if args['type'] == 2001:
			if not args['bankName'] :
				args['bankName'] = Bank.query.filter(Bank.id == args['bankId']).all()[0].name
		args = {key: value for key, value in args.items() if value is not None}
		bank_account = SystemBankAccount(**args)

		try:
			db.session.add(bank_account)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([bank_account]), 201

	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('status', type=int, location=['json','args'])
		parser.add_argument('bankId', type=int, location=['json','args'])
		parser.add_argument('amount', type=str, location=['json','args'])
		parser.add_argument('type', type=int, location=['json','args'])
		parser.add_argument('accountName', type=str, location=['json','args'])
		parser.add_argument('bankName', type=str, location=['json', 'args'])
		parser.add_argument('accountNumber', type=str, location=['json','args'])
		parser.add_argument('subbranchName', type=str, location=['json','args'])
		parser.add_argument('remark', type=str, location=['json','args'])
		parser.add_argument('validTime', type=int, location=['json','args'])
		parser.add_argument('levels', type=str, location=['json','args'])
		parser.add_argument('url', type=str, location=['json','args'])
		args = parser.parse_args(strict=True)
		if args['type'] == 2001:
			if not args['remark']:
				args['remark'] = None
			if not args['bankName'] :
				args['bankName'] = Bank.query.filter(Bank.id == args['bankId']).all()[0].name
			if args['url'] :
				args['url'] = ''
		else:
			if not args['remark']:
				args['remark'] = None
			if args['accountNumber'] :
				args['accountNumber'] = ''
			if args['subbranchName'] :
				args['subbranchName'] = ''
			if args['bankName'] :
				args['bankName'] = ''
		# args = {key: value for key, value in args.items() if value is not None}

		try:
			SystemBankAccount.query.filter(SystemBankAccount.id == id).update(args)
			db.session.commit()
			result = []
			get_all = SystemBankAccount.query.filter(SystemBankAccount.id == id).first()
			# for i in range(len(get_all)):
			get_dict = {}
			get_dict['id'] = get_all.id
			get_dict['type'] = get_all.type
			get_dict['levels'] = get_all.levels
			get_dict['accountNumber'] = get_all.accountNumber
			get_dict['accountName'] = get_all.accountName
			get_dict['url'] = get_all.url
			get_dict['validTime'] = get_all.validTime
			get_dict['bankName'] = get_all.bankName
			get_dict['subbranchName'] = get_all.subbranchName
			get_dict['status'] = get_all.status
			get_dict['amount'] = get_all.amount
			get_dict['remark'] = get_all.remark

		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response(data=[get_dict])

	def delete(self, id):
		args = {}
		args['isDelete'] = 1
		if args:
			try:
				SystemBankAccount.query.filter(SystemBankAccount.id == id).update(args)
				db.session.commit()
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)
		return make_response([])

class MemberBankAccounts(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'memberId': fields.Integer,
		'bankName': fields.String,
		'accountNumber': fields.String,
		'accountName': fields.String,
		'subbranchName': fields.String,
		'province': fields.String,
		'city': fields.String,
		'remark': fields.String
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
		parser.add_argument('memberId', type=int)
		args = parser.parse_args(strict=True)

		criterion = set()
		if args['memberId']:
			criterion.add(MemberBankAccount.memberId == args['memberId'])

		pagination = paginate(MemberBankAccount.query, criterion, args['page'], args['pageSize'])
		for item in pagination.items:
			item.bankName = item.bank.name
		return make_response_from_pagination(pagination)

	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('memberId', type=int, required=True)
		parser.add_argument('bankId', type=int, required=True)
		parser.add_argument('accountNumber', type=str, required=True)
		parser.add_argument('accountName', type=str)
		parser.add_argument('subbranchName', type=str)
		parser.add_argument('province', type=str)
		parser.add_argument('city', type=str)
		parser.add_argument('remark', type=str)
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value}
		member_bank_account_args = args
		member = Member.query.get(args['memberId'])
		if not member:
			return make_response(error_message='会员编号错误')
		if not Bank.query.get(args['bankId']):
			return make_response(error_message='银行编号错误')
		if member.bankAccount.first():
			return make_response(error_message='会员银行账户资料已存在')

		args['createTime'] = time_to_value()
		member_bank_account = MemberBankAccount(**args)
		member_bank_account_args['userId'] = g.current_user.id
		member_bank_account_args['time'] = time_to_value()
		del member_bank_account_args['createTime']
		member_bank_account_modification_log = MemberBankAccountModificationLog(**member_bank_account_args)
		try:
			db.session.add(member_bank_account)
			db.session.add(member_bank_account_modification_log)
			db.session.commit()
			OperationHistory().PublicMemberDatasApply(1003, member_bank_account.memberId)
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([]), 201

	def put(self):
		parser = RequestParser(trim=True)
		parser.add_argument('memberId', type=int, required=True)
		parser.add_argument('bankId', type=int)
		parser.add_argument('accountNumber', type=str)
		parser.add_argument('accountName', type=str)
		parser.add_argument('subbranchName', type=str)
		parser.add_argument('province', type=str)
		parser.add_argument('city', type=str)
		parser.add_argument('remark', type=str)
		args = parser.parse_args(strict=True)
		# args = {key: value for key, value in args.items() if value}

		bank_account = MemberBankAccount.query.filter(MemberBankAccount.memberId == args['memberId']).first()
		if not bank_account:
			return make_response(data=None, error_message='会员银行账户资料不存在')

		for key, value in args.items():
			setattr(bank_account, key, value)
		args['userId'] = g.current_user.id
		args['time'] = time_to_value()
		member_bank_account_modification_log = MemberBankAccountModificationLog(**args)
		try:
			db.session.add(bank_account)
			db.session.add(member_bank_account_modification_log)
			db.session.commit()
			OperationHistory().PublicMeDatas(1111, bank_account.memberId)
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])

class MemberBankAccountModificationLogs(Resource):

	@marshal_with(make_marshal_fields({
		'username': fields.String,
		'memberUsername': fields.String,
		'bankName': fields.String,
		'accountNumber': fields.String,
		'accountName': fields.String,
		'subbranchName': fields.String,
		'province': fields.String,
		'city': fields.String,
		'remark': fields.String,
		'modificationTime': fields.Integer(attribute='time'),
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
		parser.add_argument('memberId', type=int)
		args = parser.parse_args(strict=True)

		criterion = set()
		if args['memberId']:
			criterion.add(MemberBankAccountModificationLog.memberId == args['memberId'])

		pagination = paginate(MemberBankAccountModificationLog.query, criterion, args['page'], args['pageSize'])
		for item in pagination.items:
			item.username = item.user.username if item.user else None
			item.memberUsername = item.member.username
			item.bankName = item.bank.name
		return make_response_from_pagination(pagination)


