from flask import request, g
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
import time
from app.models import db
from app.models.common.utils import *
from app.models.member import Member
from app.models.audits import Audits
from app.models.member_account_change import MemberAccountChangeRecord, Deposit, Withdrawal
from app.common.utils import *
from ..common import *
from ..common.utils import *

class DepositAuditTypes(Resource):
	def get(self):
		return {
			1: '免除稽核',
			2: '存款稽核',
			3: '优惠稽核',
		}

class DepositAudits(Resource):
	
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('memberId', type=int, required=True)
		args = parser.parse_args(strict=True)
		m_data = Audits().audits(args['memberId'])
		return {"success": True,'data':m_data}

	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('auditCharge', type=float, required=True)
		args = parser.parse_args(strict=True)

		record = MemberAccountChangeRecord.query.get(id)
		if not record:
			abort(400)

		# 稽核修改，不能修改稽核类型
		# 稽核修改，只能修改稽核金额
		if record.auditType == 2 or record.auditType == 3:
			record.member.hitCodeNeed -= record.auditCharge
			record.member.hitCodeNeed += args['auditCharge']
			record.auditCharge = args['auditCharge']
			try:
				db.session.add(record)
				db.session.commit()
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)
		return make_response([])
