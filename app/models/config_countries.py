from . import db
from app.models.common.utils import *
from flask_restful import abort

class ConfigCountries(db.Model):
	__tablename__ = 'tb_config_countries_code'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	ename = db.Column(db.String)
	code = db.Column(db.String)
	state = db.Column(db.Integer,default=1)
	

	
