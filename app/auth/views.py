from flask import request, g, abort
from flask.views import MethodView
from flask.json import jsonify
import time,datetime

from app.models import db
from app.models.user import User
from app.models.member import Member
from app.models.memeber_history import OperationHistory


class Object:
	pass


class UserLogin(MethodView):
	def post(self):
		try:
			username = request.json['username']
			password = request.json['password']
		except:
			abort(400)

		user = User.query.filter(User.username == username, User.deleted != 1).first()
		if not user or not user.verify_password(password):
			abort(401)
		if user.enabled == 0:
			return jsonify({
				'success': False,
				'errorCode': 403,
				'errorMsg': '该管理员已被停用'
			})

		g.current_user = Object()
		g.current_user.id = user.id
		g.current_user.username = user.username
		a = int(time.time())
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
		try:
			user = User.query.get(g.current_user.id)
			user.lastLoginTime = a
			user.lastLoginIP = request.remote_addr
			db.session.add(user)
			db.session.commit()
			OperationHistory().UserLogin(400001, user)
		except:
			db.session.rollback()
			db.session.remove()

		return jsonify({
			'success': True,
			'token': User.generate_token(user),
			'menus': menus,
			'resources':m_resources,
			'currentUser': {
				'id': g.current_user.id,
				'username': g.current_user.username
			}
		})


class UserLogout(MethodView):
	from .common import token_auth
	decorators = [token_auth.login_required]

	def get(self):
		return jsonify({
			'success': True
		})


class UserPasswordVerification(MethodView):
	from .common import token_auth
	decorators = [token_auth.login_required]

	def get(self):
		try:
			password = request.args['password']
		except:
			abort(400)

		user = User.query.get(g.current_user.id)
		if not user or not user.verify_password(password):
			return jsonify({
				'success': False,
				'errorCode': 403,
				'errorMsg': '密码验证失败'
			})

		return jsonify({
			'success': True,
			'currentUserID': g.current_user.id,
			'currentUsername': g.current_user.username
		})

	def post(self):
		try:
			password = request.json['password']
		except:
			abort(400)

		user = User.query.get(g.current_user.id)
		if not user or not user.verify_password(password):
			return jsonify({
				'success': False,
				'errorCode': 403,
				'errorMsg': '密码验证失败'
			})

		return jsonify({
			'success': True,
			'currentUserID': g.current_user.id,
			'currentUsername': g.current_user.username
		})


class MemberLogin(MethodView):
	def post(self):
		try:
			username = request.json['username']
			password = request.json['password']
		except:
			abort(400)

		member = Member.query.filter(Member.username == username).first()
		if not member or not member.verify_password(password):
			abort(401)
		if member.status == 0:
			return jsonify({
				'success': False,
				'errorCode': 403,
				'errorMsg': '该用户已被停用'
			})

		g.current_member = Object()
		g.current_member.id = member.id
		g.current_member.username = member.username
		g.current_member.isTsetPLay = member.isTsetPLay
		return jsonify({
			'success': True,
			'token': Member.generate_token(member),
			'currentMember': {
				'id': g.current_member.id,
				'username': g.current_member.username
			}
		})


class ChatroomLogin(MethodView):
	def get(self):
		try:
			username = request.args['username']
			password = request.args['password']
		except:
			abort(400)

		user = User.query.filter(User.username == username).first()
		if not user or not user.verify_password(password):
			abort(401)
		if not user.enabled or not user.chat:
			abort(403)

		return jsonify({
			'id': user.id,
			'username': user.username,
			'nickname': user.nickname,
			'head': '/api/static/heads/' + user.head
		})

	def post(self):
		try:
			username = request.json['username']
			password = request.json['password']
		except:
			abort(400)

		user = User.query.filter(User.username == username).first()
		if not user or not user.verify_password(password):
			abort(401)
		if not user.enabled or not user.chat:
			abort(403)

		return jsonify({
			'id': user.id,
			'username': user.username,
			'nickname': user.nickname,
			'head': '/api/static/heads/' + user.head
		})
