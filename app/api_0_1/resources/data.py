from flask_restful import Resource, marshal_with, fields
from ..parsers.lotteryParsers import data_get_parser
from app.models.blast_data import BlastData
from ..common.utils import *

class DataAPI(Resource):

	def get(self):
		m_args = data_get_parser.parse_args(strict=True)
		m_type = m_args['type']
		m_orm = BlastData()
		if m_type == 34:
			json2 = m_orm.getLHCDataAndTime(m_args)
		else:
			json2 = m_orm.getDataAndTime(m_args)
		return json2 