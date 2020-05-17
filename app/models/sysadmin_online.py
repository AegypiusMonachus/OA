from app.models.common.utils import *
from flask_restful import abort
import json,random
from . import alchemyencoder
from .bank_account import SystemBankAccount
from app.models.member import Member
class SysadminOnline(db.Model):
	__tablename__ = 'blast_sysadmin_online'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	pay_type = db.Column(db.Integer)
	uid = db.Column(db.Integer)#用户id
	#bank_online_id = db.Column(db.Integer,db.ForeignKey('tb_bank_online_list.id'))
	bank_online_id = db.Column(db.Integer)
	username = db.Column(db.String)#用户名
	enable = db.Column(db.Integer)
	code = db.Column(db.String)
	secret_key = db.Column(db.String)
	tb = db.Column(db.String)
	amount = db.Column(db.Float(13, 3),default=0.000)#累计金额
	min_amount = db.Column(db.Float(13, 3))#累计金额
	max_amount = db.Column(db.Float(13, 3))#累计金额
	gradeList = db.Column(db.String)#用户等级
	validTime = db.Column(db.Integer)#有效时间
	remark = db.Column(db.String, default=None)#备注
	isDelete = db.Column(db.Integer, default=0)
	accumulatedAmount = db.Column(db.Float(13, 3))
	RecommendAmount = db.Column(db.String, default=None)#备注
	RecommendRemark = db.Column(db.String, default=None)#备注

	#bankOnline = db.relationship('BankOnline',backref=db.backref('SysadminOnline', lazy='dynamic'))

	def getData(self,criterion,pageNum,pageSize):
		m_query = db.session.query(SysadminOnline).filter(SysadminOnline.isDelete == 0)
		page = paginate(criterion=criterion,query=m_query,page=pageNum,per_page=pageSize)
		#page = db.session.query(SysadminBank).paginate(1, 20, error_out=False)
		while not page.items and page.has_prev:
			page = page.prev()
		if not page.items:
			return None
		return page

	def getdate(self,id):
		m_str = "SELECT id,name FROM `blast_sysadmin_online` where FIND_IN_SET('{}',gradeList) and isDelete =0; ".format(id)
		m_result = execute(m_str)
		return m_result

	def update(self, id, **args):
		# m_parm = {key: args[key] for key in args if args[key] is not None}
		try:
			m_res = SysadminOnline.query.filter(SysadminOnline.id == id).update(args)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)

		return m_res

	def insert(self,**args):
		dao = SysadminOnline(**args)
		try:
			db.session.add(dao)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return dao
	
	def delete(self,id):
		args = {}
		args['isDelete'] = 1
		# m_dao = SysadminOnline.query.filter(SysadminOnline.id == id).first()
		if args:
			try:
				SysadminOnline.query.filter(SysadminOnline.id == id).update(args)
				db.session.commit()
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)
		return 1	

	'''
	根据用户等级查询可使用的支付网关
	'''
# 	def getwayByGrade(self,grade):
# 		m_sql = '''select so.id,so.pay_type,so.bank_online_id,ol.bank_list,so.min_amount,so.max_amount
# 				from blast_sysadmin_online so,tb_bank_online_list ol
# 				where so.bank_online_id = ol.id and so.enable = 1 and ol.enable = 1 
# 				and FIND_IN_SET(%s,so.gradeList) =1 and so.id in (select id from blast_sysadmin_online 
# 				where FIND_IN_SET(%s,gradeList) = 1 and enable = 1 group by pay_type)'''%(grade,grade)
# 		m_result = db.session.execute(m_sql)
# 		m_json = json.loads(json.dumps([dict(r) for r in m_result],ensure_ascii=True,default=alchemyencoder))
# 		print(m_json)
# 		return m_json
	def gatewayByGrade(self,username):	
		m_sql = '''select so.id,so.pay_type,so.bank_online_id,ol.bank_list,
				so.min_amount,so.max_amount, so.RecommendAmount
				from blast_sysadmin_online so,tb_bank_online_list ol
				where so.bank_online_id = ol.id and so.enable = 1 and ol.enable = 1 and so.isDelete = 0 and (so.amount < so.accumulatedAmount or so.accumulatedAmount is Null)
				and FIND_IN_SET((select grade from blast_members where username = '%s'),so.gradeList) >0'''%(username)
		m_result = db.session.execute(m_sql)
		m_json = json.loads(json.dumps([dict(r) for r in m_result],ensure_ascii=True,default=alchemyencoder))
		#返回的数据集
		m_map = {}
		'''
		循环结果，根据支付类型(pay_type)将数据分组，每种支付类型只随机保留一个结果
		'''
		for m_row in m_json:
			m_list = []
			m_key = m_row['pay_type']
			if m_key in m_map.keys():
				#isChange = random.randint(0,1)
				#if isChange == 1:
					m_map[m_key].append(m_row)
			else:
				m_list.append(m_row)
				#online_map[m_key] = m_row
				m_map[m_key] = m_list
		online_map = {};
		for key in m_map:
			m_len = len(m_map[key])
			if m_len > 1:
				m_index = random.randint(0,m_len-1)
				online_map[key] = m_map[key][m_index]
			else:
				online_map[key] = m_map[key][0]
		#------------------公司支付----------------
		m_sql = '''select id,type as pay_type,url,bankId , username accountName ,account accountNumber,address subbranchName,
				0 min_amount,99999999 max_amount,remark,
				(select name from blast_bank_list where id = bankId) bankName 
				from blast_sysadmin_bank where enable = 1 and isDelete = 0 and FIND_IN_SET((select grade from blast_members where username = '%s'),gradeList) >0
				'''%(username)
		m_result = db.session.execute(m_sql)
		m_json = json.loads(json.dumps([dict(r) for r in m_result],ensure_ascii=True,default=alchemyencoder))
		#返回的数据集
		company_map = {}
		'''
		循环结果，根据支付类型(pay_type)将数据分组，每种支付类型只随机保留一个结果
		'''
		m_map = {}
		for m_row in m_json:
			m_list = []
			m_key = m_row['pay_type']
			if m_key in m_map.keys():
				#isChange = random.randint(0,1)
				#if isChange == 1:
					m_map[m_key].append(m_row)
			else:
				m_list.append(m_row)
				#online_map[m_key] = m_row
				m_map[m_key] = m_list
		company_map = {};
		for key in m_map:
			m_len = len(m_map[key])
			if m_len > 1:
				m_index = random.randint(0,m_len-1)
				company_map[key] = m_map[key][m_index]
			else:
				company_map[key] = m_map[key][0]
		m_result_map = {}
		m_result_map['online'] = online_map
		m_result_map['company'] = company_map
		return m_result_map

	def getGradeByUsername(self,username):
		grade = db.session.query(Member.levelConfig).filter(Member.username == username).scalar()
		return grade

