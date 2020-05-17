from flask import g, request, abort
from flask.json import jsonify
from flask_restful import Resource, marshal_with, fields
from flask_restful.reqparse import RequestParser

class PayAPI(Resource):
	from app.auth.common import token_auth
	decorators = [token_auth.login_required]

	def get(self):
		if not hasattr(g, 'current_member'):
			abort(500)

		return {
			'id': g.current_member.id,
			'username': g.current_member.username,
			'grade': g.current_member.levelConfig,
			'balance': g.current_member.balance,
		}
		
