from flask import request, g
from flask_restful import Resource, marshal_with, fields
from flask_restful.reqparse import RequestParser
from app.api_0_1.common.utils import make_marshal_fields,make_response,make_response_from_pagination
# from .. import api
from ..parsers.systemConfig import configIplist_parsers_post,configIplist_parsers_put
from app.models.config_iplist import ConfigIplist
from pickle import NONE
import json
import time
from flask.json import jsonify
from app.redis.redisConnectionManager import IPRedisManager
from app.models.memeber_history import OperationHistory
from ..common import *


class OperationHistorys(Resource):
    @marshal_with(make_marshal_fields({
        'id': fields.Integer,
        'uid': fields.Integer,
        'auditime': fields.Integer,
        'info': fields.String,
        'makeUser': fields.String,
        'orderId': fields.String,
        'contents': fields.String,
        'ip': fields.String,
        'amount': fields.Integer,
        'username': fields.String,
        'makeUserName': fields.String
}))
    def get(self):
        historys = RequestParser()
        historys.add_argument('username', type=str)
        historys.add_argument('auditimeUpper', type=int)
        historys.add_argument('auditimeLower', type=int)
        historys.add_argument('infoIn', type=str)
        historys.add_argument('infoOut', type=str)
        historys.add_argument('makeUserName', type=str)
        m_args = historys.parse_args(strict=True)
        criterion = set()
        if m_args['username']:
            criterion.add(OperationHistory.username == m_args['username'])
        if m_args['auditimeUpper']:
            criterion.add(OperationHistory.auditime < m_args['auditimeUpper'] + SECONDS_PER_DAY)
        if m_args['auditimeLower']:
            criterion.add(OperationHistory.auditime >= m_args['auditimeLower'])
        if m_args['infoIn']:
            criterion.add(OperationHistory.info.like('%{}%'.format(m_args['infoIn'])))
        if m_args['infoOut']:
            criterion.add(~OperationHistory.info.like('%{}%'.format(m_args['infoOut'])))
        if m_args['makeUserName']:
            criterion.add(OperationHistory.makeUserName == m_args['makeUserName'])
        args = OperationHistory().getdata(criterion)
        return make_response(args)