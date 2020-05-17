from flask_restful import Resource, marshal_with, fields
from flask import make_response,redirect,Response,g
from flask_restful.reqparse import RequestParser
from app.common import utils
from app.models.sysadmin_online import SysadminOnline
from app.models.bank_account import *
from app.models.payment import Payment
from app.gateway import GatewaytFactory
import json,random
from flask_restful import request
from app.gateway.abstractGateway import AbstractGateway

import time
import base64
from pyDes import *
import binascii,hashlib

class BibaoNotify(Resource):
    def GetBankCard(self):
        parser = RequestParser()
        parser.add_argument('UserName', type=str)
        parser.add_argument('OrderNum', type=str)
        parser.add_argument('Sign', type=str)
        return parser.parse_args(strict=True)

    def post(self):
        parser = self.GetBankCard()
        keyB = 'xx4gHAgm5y'
        # 按文档的要求拼拼接符串
        m_str = '''OrderNum=%s&UserName=%sxx4gHAgm5y'''%(parser['OrderNum'], parser['UserName'])
        # md5加密算法
        md = hashlib.md5()
        md.update((m_str).encode())
        m_sign = md.hexdigest().lower()
        try:
            if parser['Sign'] and parser['UserName'] and parser['OrderNum']:
                if parser['Sign'] == m_sign:
                    args = {}
                    args['Success'] = True
                    args['Code'] = 1
                    args['Message'] = '查询成功'
                    m_args = MemberBankAccount.query.filter(MemberBankAccount.accountName == parser['UserName']).first()
                    print(m_args.__dict__)
                    args['Account'] = m_args.accountNumber
                    bankId = m_args.bankId
                    args['Bank'] = Bank.query.filter(Bank.id == bankId).first().name
                    args['RealName'] = m_args.subbranchName
                    args['SubBranch'] = m_args.city
                    h_str = str(args['Account'])+str(args['Bank'])+str(args['RealName'])+str(args['SubBranch'])+keyB
                    # md5加密算法
                    md = hashlib.md5()
                    md.update((h_str).encode())
                    h_sign = md.hexdigest().lower()
                    args['Sign'] = h_sign
                    return args
                else:
                    return {'Success':False,'Code':104,'Message':'信息错误'}
            else:
                return {'Success': False, 'Code': 104, 'Message': '信息错误'}
        except:
            return {'Success': False, 'Code': 104, 'Message': '信息错误'}

