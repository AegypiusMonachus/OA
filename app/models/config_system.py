from . import db
from app.models.common.utils import *
from flask_restful import abort

class ConfigSystem(db.Model):
	__tablename__ = 'tb_config_system'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	parameter = db.Column(db.String)
	code = db.Column(db.String)
	

	
