from . import db
from app.models.common.utils import *

class Bank(db.Model):
	__tablename__ = 'blast_bank_list'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	home = db.Column(db.String)
	logo = db.Column(db.String)

	memberBankAccounts = db.relationship(
		'MemberBankAccount', backref='bank', lazy='dynamic'
	)
	memberBankAccountModificationLogs = db.relationship(
		'MemberBankAccountModificationLog', backref='bank', lazy='dynamic'
	)


class SystemBankAccount(db.Model):
	__tablename__ = 'blast_sysadmin_bank'

	id = db.Column(db.Integer, primary_key=True)
	uid = db.Column(db.Integer, default=1)
	admin = db.Column(db.Integer, default=1)
	bankId = db.Column('bankId', db.Integer, db.ForeignKey('blast_bank_list.id'))
	bankName = db.Column(db.String,default=None)
	type = db.Column(db.Integer)
	status = db.Column('enable', db.Integer, default=1)
	accountName = db.Column('username', db.String)
	accountNumber = db.Column('account', db.String,default=None)
	subbranchName = db.Column('address', db.String,default=None)
	levels = db.Column('gradeList', db.String)
	validTime = db.Column(db.Integer, default=None)
	remark = db.Column(db.String, default=None)
	url = db.Column(db.String,default=None)
	amount = db.Column(db.Float,default=0.000)
	editEnable = db.Column('editEnable', db.Integer, default=1)
	isDelete = db.Column(db.Integer, default=0)

	def getdate(self,id):
		m_str = "SELECT id,username FROM `blast_sysadmin_bank` where FIND_IN_SET('{}',gradeList) and isDelete =0; ".format(id)
		m_result = execute(m_str)
		return m_result



class MemberBankAccount(db.Model):
	__tablename__ = 'blast_member_bank'

	id = db.Column(db.Integer, primary_key=True)
	memberId = db.Column('uid', db.Integer, db.ForeignKey('blast_members.uid'))
	bankId = db.Column('bankId', db.Integer, db.ForeignKey('blast_bank_list.id'))
	accountNumber = db.Column('account', db.String)
	accountName = db.Column('username', db.String)
	subbranchName = db.Column('countName', db.String)
	province = db.Column(db.String)
	city = db.Column(db.String)
	remark = db.Column(db.String)
	createTime = db.Column('bdtime', db.Integer, default=0)
	updateTime = db.Column('xgtime', db.Integer, default=0)


class MemberBankAccountModificationLog(db.Model):
	__tablename__ = 'tb_member_bank_account_modification_logs'

	id = db.Column(db.Integer, primary_key=True)
	userId = db.Column(db.Integer, db.ForeignKey('tb_users.id'))
	memberId = db.Column(db.Integer, db.ForeignKey('blast_members.uid'))
	bankId = db.Column(db.Integer, db.ForeignKey('blast_bank_list.id'))
	accountNumber = db.Column(db.String)
	accountName = db.Column(db.String, default=None)
	subbranchName = db.Column(db.String, default=None)
	province = db.Column(db.String, default=None)
	city = db.Column(db.String, default=None)
	remark = db.Column(db.String, default=None)
	time = db.Column(db.String)
