import random

from sqlalchemy.sql import func

from app.models.common.utils import *

from . import db
from .bank_account import MemberBankAccount, MemberBankAccountModificationLog
from .member_account_change import MemberAccountChangeRecord, Deposit, Withdrawal


class Member(db.Model):
	__tablename__ = 'blast_members'

	id = db.Column('uid', db.Integer, primary_key=True)
	username = db.Column(db.String, unique=True)
	name = db.Column(db.String)
	passwordHash = db.Column('password', db.String)
	fundPasswordHash = db.Column('coinPassword', db.String)
	status = db.Column('enable', db.Integer, default=1)
	registrationTime = db.Column('regTime', db.Integer)
	registrationHost = db.Column('regIP', db.Integer)
	type = db.Column(db.Integer)
	parent = db.Column('parentId', db.Integer, default=None)
	parents = db.Column(db.String, default=None)
	parentsInfo = db.Column(db.String, default=None)
	levelConfig = db.Column('grade', db.Integer, db.ForeignKey('blast_member_level.id'),  default=1)
	balance = db.Column('coin', db.Float, default=0)
	frozenBalance = db.Column('fcoin', db.Float, default=0)
	rebateRate = db.Column('fanDian', db.Float(3, 1))
	rebate = db.Column(db.Float, default=0)
	rebateConfig = db.Column(db.Integer, db.ForeignKey('tb_config_fanshui.id'))
	commission = db.Column(db.Float)
	commissionConfig = db.Column(db.Integer, db.ForeignKey('tb_config_yongjin.id'))
	defaultRebateConfig = db.Column(db.Integer, db.ForeignKey('tb_config_fanshui.id'))
	defaultLevelConfig = db.Column(db.Integer, db.ForeignKey('blast_member_level.id'))
	hitCode = db.Column('dml', db.Float, default=0)
	hitCodeNeed = db.Column('qkdml', db.Float, default=0)
	discount = db.Column('yhje', db.Float)
	createrUsername = db.Column(db.String)
	isTsetPLay = db.Column(db.Integer, default=0)
	agentsTime = db.Column(db.Integer)
	auto_change = db.Column(db.Integer)
	isBanned = db.Column(db.Integer, default=1)
	isSuperMember = db.Column(db.Integer, default=0)
	def getLen(self, levelConfig):
		# str = "SELECT COUNT(*) FROM `blast_members` where grade={}".format(levelConfig)
		str = "select type,count(uid) FROM blast_members WHERE  isTsetPLay = 0 and grade = {} GROUP BY type  ".format(
			levelConfig)
		str = str.format(levelConfig)
		result = execute(str)
		# result = db.session.query(func.count()).filter(Member.levelConfig == levelConfig)
		return result

	def getAll(self):
		# str = "SELECT COUNT(*) FROM `blast_members` where grade={}".format(levelConfig)
		# str = "select type,count(uid) from blast_members group by type,grade having type =0 and grade = {} ORDER BY type".format(levelConfig)
		str = "select grade,count(grade) FROM blast_members WHERE type = 0 and isTsetPLay = 0 GROUP BY grade ;"
		result = execute(str)
		# result = db.session.query(func.count()).filter(Member.levelConfig == levelConfig)
		return result

	@property
	def password(self):
		raise AttributeError

	@password.setter
	def password(self, password):
		import hashlib
		self.passwordHash = hashlib.md5(password.encode()).hexdigest()

	def verify_password(self, password):
		return self.passwordHash == password

	@property
	def fundPassword(self):
		raise AttributeError

	@fundPassword.setter
	def fundPassword(self, fundPassword):
		import hashlib
		self.fundPasswordHash = hashlib.md5(fundPassword.encode()).hexdigest()

	@staticmethod
	def generate_token(member):
		from flask import current_app
		from itsdangerous import JSONWebSignatureSerializer
		serializer = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
		return serializer.dumps({'id': member.id}).decode()

	@staticmethod
	def verify_token(token):
		from flask import current_app
		from itsdangerous import JSONWebSignatureSerializer
		serializer = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
		try:
			return Member.query.get(serializer.loads(token).get('id'))
		except:
			return None

	@staticmethod
	def reset_password(username):
		member = Member.query.filter(Member.username == username).first()
		if not member:
			return None
		password = str(random.randint(00000000, 99999999))
		member.password = password
		try:
			db.session.add(member)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			return None
		return password

	@staticmethod
	def reset_fund_password(username):
		member = Member.query.filter(Member.username == username).first()
		if not member:
			return None
		password = str(random.randint(00000000, 99999999))
		member.fundPassword = password
		try:
			db.session.add(member)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			return None
		return password

	@staticmethod
	def get_all(member_id_list):
		members = []
		for member_id in member_id_list:
			member = Member.query.get(member_id)
			if member is not None:
				members.append(member)
		return members

	@staticmethod
	def get_children(member):
		if isinstance(member, str):
			member = Member.query.filter(Member.username == member).first()
		results = Member.query.filter(Member.parent == member.id).all()
		children = list(results)
		while children:
			child = children.pop()
			grandchildren = Member.query.filter(Member.parent == child.id).all()
			results.extend(grandchildren)
			children.extend(grandchildren)
		return results

	@staticmethod
	def get_parent(member):
		if isinstance(member, str):
			member = Member.query.filter(Member.username == member).first()
		return Member.query.get(member.parent)

	@staticmethod
	def update_all(members, args):
		for member in members:
			for key, value in args.items():
				if hasattr(member, key):
					setattr(member, key, value)
			db.session.add(member)
		db.session.commit()

	'''
	额度转换时使用
	'''

	@staticmethod
	def amountToMemberAccount(username, balance):
		member = Member.query.filter(Member.username == username).first()
		member.balance = member.balance + balance
		try:
			db.session.add(member)
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			db.session.remove()
			raise Exception(e)
		return member

	personalInfo = db.relationship(
		'MemberPersonalInfo', backref='member', lazy='dynamic'
	)
	bankAccount = db.relationship(
		'MemberBankAccount', backref='member', lazy='dynamic'
	)
	bankAccountModifcationLogs = db.relationship(
		'MemberBankAccountModificationLog', backref='member', lazy='dynamic'
	)
	accessLogs = db.relationship(
		'MemberAccessLog', backref='member', lazy='dynamic'
	)
	accountChangeRecords = db.relationship(
		'MemberAccountChangeRecord', backref='member', lazy='dynamic'
	)
	deposits = db.relationship(
		'Deposit', backref='member', lazy='dynamic'
	)
	withdrawals = db.relationship(
		'Withdrawal', backref='member', lazy='dynamic'
	)
	# agentAudits = db.relationship(
	# 	'AgentAudit', backref='member', lazy='dynamic'
	# )


class MemberPersonalInfo(db.Model):
	__tablename__ = 'tb_member_personal_infos'

	id = db.Column(db.Integer, db.ForeignKey('blast_members.uid'), primary_key=True)
	name = db.Column(db.String)
	gender = db.Column(db.Integer)
	birthdate = db.Column(db.Integer)
	phone = db.Column('phoneNumber', db.String)
	email = db.Column(db.String)
	tencentQQ = db.Column(db.String)
	tencentWeChat = db.Column(db.String)
	remark = db.Column(db.String, default='')


class MemberAccessLog(db.Model):
	__tablename__ = 'blast_member_session'

	id = db.Column(db.Integer, primary_key=True)
	memberId = db.Column('uid', db.Integer, db.ForeignKey('blast_members.uid'))
	username = db.Column(db.String)
	sessionKey = db.Column('session_key', db.String)
	accessTime = db.Column('loginTime', db.Integer)
	accessHost = db.Column('loginIP', db.Integer)
	realIP = db.Column(db.String)
	accessWebsite = db.Column(db.String)
	province = db.Column(db.String)
	city = db.Column(db.String)
	operator = db.Column(db.String)
	browser = db.Column(db.String)
	operatingSystem = db.Column('os', db.String)
	online = db.Column('isOnLine', db.Integer)
	country = db.Column(db.String)


class MemberLog(db.Model):
	__tablename__ = 'tb_member_logs'

	id = db.Column(db.Integer, primary_key=True)
	memberUsername = db.Column(db.String)
	time = db.Column(db.Integer)
	content = db.Column(db.String)
	orderType = db.Column(db.Integer)
	orderId = db.Column(db.Integer)
	operatorUsername = db.Column(db.String)


class MemberBatchCreateLog(db.Model):
	__tablename__ = 'tb_member_batch_create_logs'

	id = db.Column(db.Integer, primary_key=True)
	originalFilename = db.Column(db.String)
	resultFilename = db.Column(db.String)
	status = db.Column(db.Integer, default=1)
	timeBegin = db.Column(db.Integer)
	timeEnd = db.Column(db.Integer)
	operator = db.Column(db.String)
	remark = db.Column(db.String)


class AgentAudit(db.Model):
	__tablename__ = 'tb_agent_audits'

	id = db.Column(db.Integer, primary_key=True)
	memberId = db.Column(db.Integer, db.ForeignKey('blast_members.uid'))
	username = db.Column(db.String)
	password = db.Column(db.String)
	coinPassword = db.Column(db.String)
	status = db.Column(db.Integer)
	source = db.Column(db.String)
	applicationTime = db.Column(db.Integer)
	applicationHost = db.Column(db.Integer)
	auditUser = db.Column(db.Integer, db.ForeignKey('tb_users.id'))
	auditTime = db.Column(db.Integer)
	auditHost = db.Column(db.Integer)
	personinfo_name = db.Column(db.String)
	personinfo_gender = db.Column(db.Integer)
	personinfo_phone = db.Column(db.String)
	personinfo_email = db.Column(db.String)
	personinfo_birthdate = db.Column(db.Integer)
	personinfo_tencentWeChat = db.Column(db.String)
	personinfo_tencentQQ = db.Column(db.String)
	personinfo_remark = db.Column(db.String)
	bank_Id = db.Column(db.Integer)
	bank_province = db.Column(db.String)
	bank_city = db.Column(db.String)
	bank_accountNumber = db.Column(db.String)
	bank_accountName = db.Column(db.String)
	remark = db.Column(db.String)
