from . import db

class RebateLog(db.Model):
	__tablename__ = 'tb_rebate_logs'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	time = db.Column(db.Integer)
	rebateTimeLower = db.Column(db.Integer)
	rebateTimeUpper = db.Column(db.Integer)
	agentUsername = db.Column(db.String)
	operatorUsername = db.Column(db.String)
	resultFilename = db.Column(db.String)

	details = db.relationship(
		'RebateLogDetail', backref='rebateLog', lazy='dynamic'
	)

class RebateLogDetail(db.Model):
	__tablename__ = 'tb_rebate_log_details'

	rebateId = db.Column(db.Integer, db.ForeignKey('tb_rebate_logs.id'), primary_key=True)
	memberId = db.Column(db.Integer, db.ForeignKey('blast_members.uid'), primary_key=True)
	rebateAmount = db.Column('amount', db.Float)
	rebateStatus = db.Column('status', db.Integer)

class RebateDetail(db.Model):
	__tablename__ = 'tb_rebate_details'

	id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.Integer)
	memberUsername = db.Column(db.String)
	supplierName = db.Column(db.String)
	gameName = db.Column(db.String)
	betAmount = db.Column(db.Float)
	rebateAmount = db.Column(db.Float)

class CommissionLog(db.Model):
	__tablename__ = 'tb_commission_logs'

	id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.Integer)
	commissionTimeLower = db.Column(db.Integer)
	commissionTimeUpper = db.Column(db.Integer)
	agentUsername = db.Column(db.String)
	numberOfChildren = db.Column(db.Integer)
	numberOfValidBet = db.Column(db.Float)
	commission = db.Column(db.Float)
	profitAndLoss = db.Column(db.Float)
	operatorUsername = db.Column(db.String)
	resultFilename = db.Column(db.String)

class ImportDiscountLog(db.Model):
	__tablename__ = 'tb_import_discount_logs'

	id = db.Column(db.Integer, primary_key=True)
	originalFilename = db.Column(db.String)
	status = db.Column(db.Integer)
	timeLower = db.Column(db.Integer)
	timeUpper = db.Column(db.Integer)
	operatorUsername = db.Column(db.String)
	resultFilename = db.Column(db.String)
	failcount = db.Column(db.Integer)
