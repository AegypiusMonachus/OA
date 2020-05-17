from . import db
from flask_restful import abort
from sqlalchemy.sql import func
from app.models.common.utils import *
import decimal, datetime,time
import json
#from .member import MemberBankAccountModificationLog

class BankOnline(db.Model):
	__tablename__ = 'tb_bank_online_list'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	pay_url = db.Column(db.String)
	accounts_url = db.Column(db.String)
	logo_url = db.Column(db.String)
	sort = db.Column(db.Integer)
	enable = db.Column(db.Integer)
	remark = db.Column(db.String)
	modify_time = db.Column(db.String)
	
	def getData(self,id,page,per_page,grade):
		m_sql = "select id,name,pay_url,accounts_url,logo_url,sort,enable,remark,unix_timestamp(modify_time) modify_time from tb_bank_online_list"
		if id is not None:
			m_sql += " where id = %s"%(id)
		elif grade is not None:
			m_sql += " where FIND_IN_SET(%s,so.gradeList) >0 and enable = 1"%(grade) 
		m_result = execute(m_sql,page,per_page)
		return m_result	
	
	def update(self, id, **args):
		m_parm = {key: args[key] for key in args if args[key] is not None}
		try:
			m_res = BankOnline.query.filter(BankOnline.id == id).update(m_parm)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)

		return m_res

	def insert(self,**args):
		dao = BankOnline(**args)
		try:
			db.session.add(dao)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return dao

	def delete(self,id):
		m_dao = BankOnline.query.filter(BankOnline.id == id).first()
		if m_dao:
			try:
				db.session.delete(m_dao)
				db.session.commit()
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)
		return 1	

	'''
	获取所有支付网关的map集合
	'''
	def getMapList(self,name):
		m_paytypeMap={};
		m_sql = "select code,name from tb_dic where type = 900001"
		m_res = db.session.execute(m_sql)
		for m_type in m_res:
			#m_paytype.append(m_type.code);
			m_paytypeMap[m_type.code] = []
		m_sql = "select id,name,pay_type from tb_bank_online_list where enable = 1 "
		if name is not None:
			m_sql += 'and name like "%%%s%%"'%(name)
		m_res = db.session.execute(m_sql)
		for m_row in m_res:
			m_typeList = m_row.pay_type.split(",")
			m_map = {}
			m_map['id'] = m_row.id
			m_map['name'] = m_row.name
			for m_type in m_typeList:
				m_paytypeMap[int(m_type)].append(m_map)
		return m_paytypeMap;	
	
		