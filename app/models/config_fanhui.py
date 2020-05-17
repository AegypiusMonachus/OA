from . import db
from app.models.common.utils import *
from flask_restful import abort
from .member import Member

class ConfigFanshui(db.Model):
	__tablename__ = 'tb_config_fanshui'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, default=0)
	dml = db.Column(db.Float, default=0)
	fsb = db.Column(db.String)
	sx = db.Column(db.Float)
	jh = db.Column(db.Float)
	ss_enable = db.Column(db.Integer)
	pc_enable = db.Column(db.Integer, default=2)
	ss_zdlqxe = db.Column(db.Float)
	ss_zglqxe = db.Column(db.Float)
	ss_jh = db.Column(db.Float)
	ylc = db.Column(db.String)
	fsmx = db.Column(db.String)
	remark = db.Column(db.String, default=None)
	fs_type = db.Column(db.Integer, default=2)       # 1.时时返还 2.手动返还

	members_with_rebate_config = db.relationship(
		'Member', foreign_keys=[Member.rebateConfig], backref='rebate_config', lazy='dynamic')
	members_with_default_rebate_config = db.relationship(
		'Member', foreign_keys=[Member.defaultRebateConfig], backref='default_rebate_config', lazy='dynamic')

	def getData(self,criterion,pageNum,pageSize):
		m_query = db.session.query(ConfigFanshui)
		page = paginate(criterion=criterion,query=m_query,page=pageNum,per_page=pageSize)
		#page = db.session.query(SysadminBank).paginate(1, 20, error_out=False)
		while not page.items and page.has_prev:
			page = page.prev()
		if not page.items:
			return None
		return page	

	def update(self, id, **args):
		m_parm = {key: args[key] for key in args if args[key] is not None}
		try:
			m_res = ConfigFanshui.query.filter(ConfigFanshui.id == id).update(m_parm)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return m_res

	def insert(self,**args):
		dao = ConfigFanshui(**args)
		try:
			db.session.add(dao)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return dao

	def delete(self,id):
		m_dao = ConfigFanshui.query.filter(ConfigFanshui.id == id).first()
		if m_dao:
			try:
				db.session.delete(m_dao)
				db.session.commit()
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)
		return 1
class ConfigFanshuiPc(db.Model):
	__tablename__ = 'tb_config_fanshui_pc'
	id = db.Column(db.Integer, primary_key=True)
	# fs_id = db.Column(db.Integer, db.ForeignKey("tb_config_fanshui.id"))  # 表名.字段名
	fs_id = db.Column(db.Integer)
	pc_dml = db.Column(db.Float,default=0)
	pc_sx = db.Column(db.Float,default=0)
	pc_jh = db.Column(db.Float,default=0)
	pc_fsb = db.Column(db.String)