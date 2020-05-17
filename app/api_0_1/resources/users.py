from flask import request, g
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
from werkzeug.security import generate_password_hash,check_password_hash

from app.models import *
from app.models.common.utils import *
from app.models.user import User, Role, Menu
from app.common.utils import *
from ..common import *
from ..common.utils import *
from flask.json import jsonify
import re

class Users(Resource):
	from app.auth.common import token_auth
	decorators = [token_auth.login_required]

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'username': fields.String,
		'enabled': fields.Integer,
		'deleted': fields.Integer,
		'registrationTime': fields.Integer,
		'registrationHost': fields.Integer,
		'phone': fields.String,
		'email': fields.String,
		'google':fields.String,
		'verificationByPhone': fields.Integer,
		'verificationByGoogle': fields.Integer,
		'verificationByEmail': fields.Integer,
		'accumulatedSystemDeposit': fields.Float,
		'systemDepositLimitOnce': fields.Float,
		'systemDepositLimitTotal': fields.Float,
		'systemDepositLimitCount': fields.Float,
		'lastLoginTime': fields.Integer,
		'lastLoginIP': fields.String,
		'withdrawallimitOnce': fields.Float,
		'withdrawallimitSumCeiling': fields.Float,
		'withdrawallimitSum': fields.Float,
		'chat': fields.Integer,
		'remark': fields.String,
		'menus': fields.List(fields.Nested({
			'menuId': fields.Integer(attribute='id'),
			'menuName': fields.String(attribute='name'),
			'menuParentId': fields.Integer(attribute='parent'),
			'menuParentName': fields.String(attribute='parent_name'),
			'menutype': fields.String(attribute='type'),
			'menuaddress': fields.String(attribute='address'),
			'menuapiUrl': fields.String(attribute='api_url'),
		}))
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
		parser.add_argument('username', type=str)
		args = parser.parse_args(strict=True)

		criterion = set()
		criterion.add(User.deleted == 0)
		if args['username']:
			criterion.add(User.username == args['username'])

		pagination = paginate(User.query, criterion, args['page'], args['pageSize'])
		for item in pagination.items:
			for menu in item.menus:
				parent = Menu.query.filter(Menu.id == menu.parent).first()
				if parent:
					menu.parent_name = parent.name
		return make_response_from_pagination(pagination)

	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('username', type=str, required=True)
		parser.add_argument('password', type=str, required=True)
		parser.add_argument('phone', type=str)
		parser.add_argument('email', type=str)
		parser.add_argument('google', type=str)
		parser.add_argument('verificationByPhone', type=int)
		parser.add_argument('verificationByEmail', type=int)
		parser.add_argument('verificationByGoogle', type=int)
		parser.add_argument('systemDepositLimitOnce', type=float)
		parser.add_argument('systemDepositLimitTotal', type=float)
		parser.add_argument('withdrawallimitOnce', type=float)
		parser.add_argument('withdrawallimitSumCeiling', type=float)
		parser.add_argument('chat', type=int)
		parser.add_argument('remark', type=str)
		parser.add_argument('menus', type=str )
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value is not None}

		u = User.query.filter(User.username == args['username']).first()
		if u:
			return make_response(error_message='子账户名已存在')
		if 'menus' not in args:
			return {"errorCode":400,"errorMsg":"请选择新用户权限"}
		menu_id_list = args.pop('menus').split(',')
		try:
			user = User(**args)
			user.registrationTime = time_to_value()
			user.registrationHost = host_to_value(request.remote_addr)
			db.session.add(user)
			db.session.commit()
			try:
				for menu_id in menu_id_list:
					menu = Menu.query.get(menu_id)
					if menu:
						user.menus.append(menu)
				db.session.add(user)
				db.session.commit()
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([]), 201

	@marshal_with(make_marshal_fields({
		'password': fields.String
	}))
	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('enabled', type=int)
		parser.add_argument('chat', type=int)
		parser.add_argument('verificationByPhone', type=int)
		parser.add_argument('verificationByGoogle', type=int)
		parser.add_argument('verificationByEmail', type=int)
		parser.add_argument('oldPassword', type=str)
		parser.add_argument('newPassword', type=str)
		parser.add_argument('phone', type=str)
		parser.add_argument('email', type=str)
		parser.add_argument('menus', type=str)
		parser.add_argument('systemDepositLimitOnce', type=str)
		parser.add_argument('systemDepositLimitCount', type=str)
		parser.add_argument('systemDepositLimitTotal', type=int)
		parser.add_argument('withdrawallimitOnce', type=str)
		parser.add_argument('withdrawallimitSumCeiling', type=str)
		parser.add_argument('withdrawallimitSum', type=int)
		parser.add_argument('remark', type=str)
		args = parser.parse_args(strict=True)

		user = User.query.get(id)
		if not user:
			abort(400)
		if args['enabled'] is not None:
			user.enabled = args['enabled']
		if args['chat'] is not None:
			user.chat = args['chat']
		if args['verificationByPhone'] is not None:
			user.verificationByPhone = args['verificationByPhone']
		if args['verificationByGoogle'] is not None:
			user.verificationByGoogle = args['verificationByGoogle']
		if args['verificationByEmail'] is not None:
			user.verificationByEmail = args['verificationByEmail']

		if args['oldPassword'] and args['newPassword']:

			if not user.verify_password(args['oldPassword']):
				return make_response(error_code=400, error_message="旧密码输入错误")
			if args['oldPassword'] == args['newPassword']:
				return make_response(error_code=400, error_message="新旧密码一致")

			pattern = "^[A-Za-z0-9]{6,15}$"
			re_result = re.match(pattern, args['newPassword'])
			if re_result is None:
				return make_response(error_code=400, error_message="新密码格式不正确")
			if user.verify_password(args['oldPassword']):
				user.password = args['newPassword']

		if args['phone']:
			user.phone = args['phone']
		if args['email']:
			user.email = args['email']
		if args['systemDepositLimitOnce']:
			user.systemDepositLimitOnce = args['systemDepositLimitOnce']
		if args['systemDepositLimitCount']:
			user.systemDepositLimitCount = args['systemDepositLimitCount']
		if args['systemDepositLimitTotal'] is not None:
			user.systemDepositLimitTotal = args['systemDepositLimitTotal']

		if args['withdrawallimitOnce']:
			user.withdrawallimitOnce = args['withdrawallimitOnce']
		if args['withdrawallimitSumCeiling']:
			user.withdrawallimitSumCeiling = args['withdrawallimitSumCeiling']
		if args['withdrawallimitSum'] is not None:
			user.withdrawallimitSum = args['withdrawallimitSum']
		if args['remark']:
			user.remark = args['remark']
		if args['menus'] == "":
			return {"errorCode": 400, "errorMsg": "请选择用户权限"}
		if args['menus']:
			user.menus.clear()
			db.session.commit()

			menu_id_list = args.pop('menus').split(',')
			for menu_id in menu_id_list:
				menu = Menu.query.get(menu_id)
				if menu and menu not in user.menus:
					user.menus.append(menu)

		try:
			db.session.add(user)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([{
			'password': args.get('newPassword')
		}])

	def delete(self, id):
		user = User.query.get(id)
		if not user:
			return make_response(error_message='子账户名不存在')
		user.deleted = 1
		try:
			db.session.add(user)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return {"success": True}

class CurrentUser(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'username': fields.String,
		'registrationTime': fields.Integer,
		'registrationHost': fields.Integer,
		'phone': fields.String,
		'email': fields.String,
		'verificationByPhone': fields.Integer,
		'verificationByEmail': fields.Integer,
		'accumulatedSystemDeposit': fields.Float,
		'systemDepositLimitOnce': fields.Float,
		'systemDepositLimitTotal': fields.Float,
	}))
	def get(self):
		if not hasattr(g, 'current_user') or not g.current_user:
			abort(500)
		user = User.query.get(g.current_user.id)
		return make_response([user])

	def put(self):
		parser = RequestParser(trim=True)
		parser.add_argument('oldPassword', type=str)
		parser.add_argument('newPassword', type=str)
		parser.add_argument('phone', type=str)
		parser.add_argument('username', type=str,required=True)
		parser.add_argument('email', type=str)
		args = parser.parse_args(strict=True)


		user = User.query.filter(User.username == args['username']).first()

		if args['phone']:
			user.phone = args['phone']
			try:
				db.session.add(user)
				db.session.commit()
				return {"success": True, "message": "修改成功"}
			except:
				db.session.rollback()
				db.session.remove()
				return {"success": False, "errorMsg": "修改失败"}

		if args['email']:
			user.email = args['email']
			try:
				db.session.add(user)
				db.session.commit()
				return {"success": True, "message": "修改成功"}
			except:
				db.session.rollback()
				db.session.remove()
				return {"success": False, "errorMsg": "修改失败"}

		if args['oldPassword'] and args['newPassword']:
			password = user.passwordHash  # 原密码
			jiu = generate_password_hash(args['oldPassword'])
			check = check_password_hash(password,args['oldPassword'])
			if check:
				user.password =	args['newPassword']
				try:
					db.session.add(user)
					db.session.commit()
					return {"success": True, "message": "修改成功"}
				except:
					db.session.rollback()
					db.session.remove()
					return {"success": False, "errorMsg": "修改失败"}

			else:
				return jsonify({
						'success': False,
						'errorCode': 403,
						'errorMsg': '原密码错误'
					})




class RoleTypes(Resource):
	def get(self):
		return {
			1: '会员',
			2: '代理',
			3: '财务管理',
			4: '系统管理',
			5: '会员端设定',
			6: '各式报表',
		}

class Roles(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'name': fields.String,
		'chineseName': fields.String,
		'type': fields.Integer,
		'description': fields.String,
	}))
	def get(self):
		return make_response(Role.query.all())

class Menus(Resource):
	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'name': fields.String,
		'code': fields.String,
		'parent': fields.Integer,
		'parentName': fields.String,
		'address': fields.String,
		'type': fields.Integer,
		'api_url': fields.String,
		'remark': fields.String
	}))
	def get(self):
		menus = Menu.query.all()
		for menu in menus:
			if menu.parent:
				parent = Menu.query.get(menu.parent)
				if parent:
					menu.parentName = parent.name
		return make_response(menus)

	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('name', type=str, required=True)
		parser.add_argument('parentName', type=str)
		args = parser.parse_args(strict=True)

		menu = Menu()
		menu.name = args['name']
		if args['parentName']:
			parent = Menu.query.filter(Menu.name == args['parentName']).first()
			if parent:
				menu.parent = parent.id
		try:
			db.session.add(menu)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)

"""１．已累计人工存入额度
　２．　归零累计
　　"""
class UserAuthority(Resource):

	def get(self):
		username = g.current_user.username
		user = User.query.filter(User.username == username).first()
		menus = []
		m_resources = []
		for menu in user.menus:
			if menu.type == 1:
				menus.append({
					'menuId': menu.id,
					'menuName': menu.name,
					'menuParent': menu.parent,
					'menuAddress': menu.address
				})
			else:
				m_resources.append(menu.id)
		return {
			'success': True,
			'menus': menus,
			'resources':m_resources,
		}	

