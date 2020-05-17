from . import db
from .member import MemberBankAccountModificationLog, AgentAudit

'''
identities = db.Table(
	'tb_user_identities',
	db.Column('userId', db.Integer, db.ForeignKey('tb_users.id')),
	db.Column('roleId', db.Integer, db.ForeignKey('tb_roles.id'))
)
'''

identities = db.Table(
	'tb_user_menus',
	db.Column('userId', db.Integer, db.ForeignKey('tb_users.id')),
	db.Column('menuId', db.Integer, db.ForeignKey('tb_menus.id'))
)

class User(db.Model):
	__tablename__ = 'tb_users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, unique=True)
	passwordHash = db.Column('password', db.String)
	enabled = db.Column(db.Integer, default=1)
	deleted = db.Column(db.Integer, default=0)
	registrationTime = db.Column(db.Integer)
	registrationHost = db.Column(db.Integer)
	phone = db.Column(db.String)
	email = db.Column(db.String)
	google = db.Column(db.String)
	verificationByGoogle = db.Column(db.Integer)
	verificationByPhone = db.Column(db.Integer)
	verificationByEmail = db.Column(db.Integer)
	accumulatedSystemDeposit = db.Column(db.Float)
	systemDepositLimitOnce = db.Column(db.Float)
	systemDepositLimitTotal = db.Column(db.Float)
	systemDepositLimitCount = db.Column(db.Float)
	lastLoginTime = db.Column(db.Integer)
	lastLoginIP = db.Column(db.String)
	withdrawallimitOnce = db.Column(db.Float)
	withdrawallimitSumCeiling = db.Column(db.Float)
	withdrawallimitSum = db.Column(db.Float)
	chat = db.Column(db.Integer, default=0)
	remark = db.Column(db.String)
	nickname = db.Column(db.String, default=None)
	head = db.Column(db.String, default=None)

	'''
	roles = db.relationship(
		'Role', secondary=identities, backref=db.backref('users', lazy='dynamic')
	)
	'''
	menus = db.relationship(
		'Menu', secondary=identities, backref=db.backref('users', lazy='dynamic')
	)
	accessLogs = db.relationship(
		'UserAccessLog', backref='user', lazy='dynamic'
	)
	operationLogs = db.relationship(
		'UserOperationLog', backref='user', lazy='dynamic'
	)
	memberBankAccountModificationLogs = db.relationship(
		'MemberBankAccountModificationLog', backref='user', lazy='dynamic'
	)
	agentAudits = db.relationship(
		'AgentAudit', backref='user', lazy='dynamic'
	)

	@property
	def password(self):
		raise AttributeError

	@password.setter
	def password(self, password):
		from werkzeug.security import generate_password_hash
		self.passwordHash = generate_password_hash(password)

	def verify_password(self, password):
		from werkzeug.security import check_password_hash
		return check_password_hash(self.passwordHash, password)

	@staticmethod
	def generate_token(user):
		from flask import current_app
		from itsdangerous import JSONWebSignatureSerializer
		serializer = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
		return serializer.dumps({'id': user.id}).decode()

	@staticmethod
	def verify_token(token):
		from flask import current_app
		from itsdangerous import JSONWebSignatureSerializer
		serializer = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
		try:
			return User.query.get(serializer.loads(token).get('id'))
		except:
			return None

class Role(db.Model):
	__tablename__ = 'tb_roles'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	chineseName = db.Column(db.String)
	type = db.Column(db.Integer)
	description = db.Column(db.String)

class Menu(db.Model):
	__tablename__ = 'tb_menus'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	code = db.Column(db.String)
	parent = db.Column(db.Integer)
	address = db.Column(db.String)
	code = db.Column(db.String)
	type = db.Column(db.Integer)
	api_url = db.Column(db.String)
	remark = db.Column(db.String)

class UserAccessLog(db.Model):
	__tablename__ = 'tb_user_access_logs'

	id = db.Column(db.Integer, primary_key=True)
	userId = db.Column(db.Integer, db.ForeignKey('tb_users.id'))
	time = db.Column(db.Integer)
	host = db.Column(db.Integer)
	userAgent = db.Column(db.String)

class UserOperationLog(db.Model):
	__tablename__ = 'tb_user_operation_logs'

	id = db.Column(db.Integer, primary_key=True)
	userId = db.Column(db.Integer, db.ForeignKey('tb_users.id'))
	target = db.Column(db.Integer)
	time = db.Column(db.Integer)
	host = db.Column(db.Integer)
	userAgent = db.Column(db.String)
	type = db.Column(db.Integer)
