from . import db
from app.models.common.utils import *
from flask_restful import abort

#会员端
class ConfigMemberService(db.Model):
	__tablename__ = 'tb_config_member_service'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	pmd = db.Column(db.String)
	member_reg = db.Column(db.String)
	agent_reg = db.Column(db.String)
	remark = db.Column(db.String)

	def getData(self,criterion):
		m_query = db.session.query(ConfigMemberService)
		page = paginate(criterion=criterion,query=m_query,page=1,per_page=30)
		#page = db.session.query(SysadminBank).paginate(1, 20, error_out=False)
		while not page.items and page.has_prev:
			page = page.prev()
		if not page.items:
			return None
		return page	

	def update(self, id, **args):
		m_parm = {key: args[key] for key in args if args[key] is not None}
		if 'member_reg' in m_parm:
			m_parm['member_reg'] = m_parm['member_reg'].replace("'", '"')
		if 'agent_reg' in m_parm:
			m_parm['agent_reg'] = m_parm['agent_reg'].replace("'", '"')
		try:
			m_res = ConfigMemberService.query.filter(ConfigMemberService.id == id).update(m_parm)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return m_res

	def insert(self,**args):
		dao = ConfigMemberService(**args)
		try:
			db.session.add(dao)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return dao

	def delete(self,id):
		m_dao = ConfigMemberService.query.filter(ConfigMemberService.id == id).first()
		if m_dao:
			try:
				db.session.delete(m_dao)
				db.session.commit()
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)
		return 1

	
