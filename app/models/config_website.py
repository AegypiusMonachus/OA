from . import db
from app.models.common.utils import *
from flask_restful import abort

class ConfigWebsite(db.Model):
	__tablename__ = 'tb_config_website'
	id = db.Column(db.Integer, primary_key=True)
	webName = db.Column(db.String)
	agentName = db.Column(db.String)
	loginVerified = db.Column(db.Integer)
	regVerified = db.Column(db.Integer)
	regQAVerified = db.Column(db.Integer)
	errorCount = db.Column(db.Integer)
	puzzleVerifiedLogin = db.Column(db.Integer)
	puzzleVerifiedReg = db.Column(db.Integer)
	landingAreaVerification = db.Column(db.Integer)
	

	def getData(self,criterion):
		m_query = db.session.query(ConfigWebsite)
		pagination = paginate(m_query, criterion, 1, 1)
		return pagination

	def update(self, id, **args):
		m_parm = {key: args[key] for key in args if args[key] is not None}
		try:
			m_res = ConfigWebsite.query.filter(ConfigWebsite.id == id).update(m_parm)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return m_res

class WebsiteSetting(db.Model):
	__tablename__ = 'tb_config_website_basic'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	website = db.Column(db.String)
	defAgentId = db.Column('def_agent_id', db.Integer)
	defAgentName = db.Column('def_agent_name', db.String)
	memberServiceId = db.Column('member_service_id', db.Integer, db.ForeignKey('tb_config_member_service.id'))
	regExamine = db.Column('reg_examine', db.Integer, default=1)
	remark = db.Column(db.String)