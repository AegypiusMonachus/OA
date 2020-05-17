from flask_restful import Resource, marshal_with, fields
from flask_restful.reqparse import RequestParser
from app.api_0_1.common.utils import make_marshal_fields,make_response,make_response_from_pagination
from .. import api
from app.api_0_1.parsers.systemConfig import member_level_parsers, member_level_parser
from app.models.member_level import MemberLevel
import json
from app.models.sysadmin_online import SysadminOnline
from app.models.bank_account import SystemBankAccount
from app.models.member import Member

# from app.common.utils import *
# from ..common import *
# from ..common.utils import *
# import json
# from datetime import datetime

fields = make_marshal_fields({
        'id': fields.Integer,
        'level': fields.String,
        'levelName': fields.String,
        'min_rk': fields.Float,
        'max_rk': fields.Float,
        'min_tk': fields.Float,
        'max_tk': fields.Float,
        'sx_Free': fields.Float,    
        'mcfy': fields.Integer,        
        'tksc': fields.Integer,            
        'ms': fields.Integer,
        'js': fields.Integer,
        'dkzfsxf': fields.String,
        'gsrkyh': fields.String,
        'xszfyh': fields.String,
        'zcscj': fields.String,
        'kscz': fields.String,
        'ckjhb':fields.String,
        'xz_Free': fields.Float,                
        'remark': fields.String,
        'danger': fields.Integer,
        'zfbmqckzt': fields.Integer,
        'isBanned': fields.Integer,
        # 'memberCount': fields.Integer,
    })

class MemberlevelAPI(Resource):
    @marshal_with(fields)
    def get(self, id=None):
        m_args = member_level_parsers.parse_args(strict=True)
        criterion = set()
        if id:
            criterion.add(MemberLevel.id == id)
        m_result = MemberLevel().getData(criterion,m_args['page'],m_args['pageSize'])
        for item in m_result.items:
            if item.xszfyh != None:
                xszfyh = json.loads(item.xszfyh)
                for xszfyh_one in xszfyh:
                    if xszfyh_one['yhbl'] != '':
                        xszfyh_one['yhbl'] = str(float('%.2f' % (float(xszfyh_one['yhbl']) * 100)))
                xszfyh = json.dumps(xszfyh)
                item.xszfyh = xszfyh
            if item.gsrkyh != None:
                gsrkyh = json.loads(item.gsrkyh)
                for gsrkyh_one in gsrkyh:
                    if gsrkyh_one['yhbl'] != '':
                        gsrkyh_one['yhbl'] = str(float('%.2f' % (float(gsrkyh_one['yhbl']) * 100)))
                gsrkyh = json.dumps(gsrkyh)
                item.gsrkyh = gsrkyh
            if item.ckjhb != None:
                ckjhb = json.loads(item.ckjhb)
                # for gsrkyh_one in gsrkyh:
                if ckjhb['gsrk'] != '':
                    ckjhb['gsrk'] = str(float('%.2f' % (float(ckjhb['gsrk']) * 100)))
                if ckjhb['xszf'] != '':
                    ckjhb['xszf'] = str(float('%.2f' % (float(ckjhb['xszf']) * 100)))
                if ckjhb['dkzf'] != '':
                    ckjhb['dkzf'] = str(float('%.2f' % (float(ckjhb['dkzf']) * 100)))
                ckjhb = json.dumps(ckjhb)
                item.ckjhb = ckjhb
            if item.dkzfsxf != None:
                dkzfsxf = json.loads(item.dkzfsxf)
                # for gsrkyh_one in gsrkyh:
                if dkzfsxf['fybl'] != '':
                    dkzfsxf['fybl'] = str(float('%.2f' % (float(dkzfsxf['fybl']) * 100)))
                dkzfsxf = json.dumps(dkzfsxf)
                item.dkzfsxf = dkzfsxf
            if item.xz_Free != None:
                item.xz_Free = float('%.2f' % (float(item.xz_Free * 100)))


        return make_response_from_pagination(m_result)
        # m_result = m_result.items
        # # print(m_result.items)
        # return make_response(data=m_result)
    
    @marshal_with(fields)
    def post(self):
        m_args = member_level_parsers.parse_args(strict=True)
        '''公司入款优惠换算'''
        if 'gsrkyh' in m_args and m_args['gsrkyh']:
            gsrkyh = json.loads(m_args['gsrkyh'])
            for i in range(len(gsrkyh)):
                if gsrkyh[i]['yhbl'] != '':
                    gsrkyh[i]['yhbl'] = str(float(gsrkyh[i]['yhbl']) / 100)
            m_args['gsrkyh'] = json.dumps(gsrkyh)
        '''线上支付优惠换算'''
        if 'xszfyh' in m_args and m_args['xszfyh']:
            xszfyh = json.loads(m_args['xszfyh'])
            for i in range(len(xszfyh)):
                if xszfyh[i]['yhbl'] != '':
                    xszfyh[i]['yhbl'] = str(float(xszfyh[i]['yhbl']) / 100)
            m_args['xszfyh'] = json.dumps(xszfyh)
        '''点卡支付手续费'''
        if 'dkzfsxf' in m_args and m_args['dkzfsxf']:
            dkzfsxf = json.loads(m_args['dkzfsxf'])
            if dkzfsxf['fybl'] != '':
                dkzfsxf['fybl'] = str(float(dkzfsxf['fybl']) / 100)
            # for i in range(len(xszfyh)):
            #     xszfyh[i]['yhbl'] = str(int(xszfyh[i]['yhbl']) / 100)
            m_args['dkzfsxf'] = json.dumps(dkzfsxf)
        '''存款稽核比'''
        if 'ckjhb' in m_args and m_args['ckjhb']:
            ckjhb = json.loads(m_args['ckjhb'])
            if ckjhb['gsrk'] != '':
                ckjhb['gsrk'] = str(float(ckjhb['gsrk']) / 100)
            if ckjhb['xszf'] != '':
                ckjhb['xszf'] = str(float(ckjhb['xszf']) / 100)
            if ckjhb['dkzf'] != '':
                ckjhb['dkzf'] = str(float(ckjhb['dkzf']) / 100)
            m_args['ckjhb'] = json.dumps(ckjhb)
        '''行政费用比'''
        if 'xz_Free' in m_args and m_args['xz_Free']:
            m_args['xz_Free'] = m_args['xz_Free'] / 100
        del m_args['page']
        del m_args['pageSize']
        args = MemberLevel.query.filter(MemberLevel.levelName == m_args['levelName']).all()
        if args:
            return {'success':False,'errorMsg':'会员等级已存在'},400
        m_res = MemberLevel().insert(**m_args)
        return make_response(data=[m_res], page=1, pages=1, total=1)
    
    def put(self, id):
        m_args = member_level_parser.parse_args(strict=True)
        '''公司入款优惠换算'''
        if 'gsrkyh' in m_args and m_args['gsrkyh']:
            gsrkyh = json.loads(m_args['gsrkyh'])
            for i in range(len(gsrkyh)):
                if gsrkyh[i]['yhbl'] != '':
                    gsrkyh[i]['yhbl'] = str(float(gsrkyh[i]['yhbl']) / 100)
            m_args['gsrkyh'] = json.dumps(gsrkyh)
        '''线上支付优惠换算'''
        if 'xszfyh' in m_args and m_args['xszfyh']:
            xszfyh = json.loads(m_args['xszfyh'])
            for i in range(len(xszfyh)):
                if xszfyh[i]['yhbl'] != '':
                    xszfyh[i]['yhbl'] = str(float(xszfyh[i]['yhbl']) / 100)
            m_args['xszfyh'] = json.dumps(xszfyh)
        '''点卡支付手续费'''
        if 'dkzfsxf' in m_args and m_args['dkzfsxf']:
            dkzfsxf = json.loads(m_args['dkzfsxf'])
            if dkzfsxf['fybl'] != '':
                dkzfsxf['fybl'] = str(float(dkzfsxf['fybl']) / 100)
            # for i in range(len(xszfyh)):
            #     xszfyh[i]['yhbl'] = str(int(xszfyh[i]['yhbl']) / 100)
            m_args['dkzfsxf'] = json.dumps(dkzfsxf)
        '''存款稽核比'''
        if 'ckjhb' in m_args and m_args['ckjhb']:
            ckjhb = json.loads(m_args['ckjhb'])
            if ckjhb['gsrk'] != '':
                ckjhb['gsrk'] = str(float(ckjhb['gsrk']) / 100)
            if ckjhb['xszf'] != '':
                ckjhb['xszf'] = str(float(ckjhb['xszf']) / 100)
            if ckjhb['dkzf'] != '':
                ckjhb['dkzf'] = str(float(ckjhb['dkzf']) / 100)
            m_args['ckjhb'] = json.dumps(ckjhb)
        '''行政费用比'''
        if 'xz_Free' in m_args and m_args['xz_Free']:
            m_args['xz_Free'] = m_args['xz_Free'] / 100
        args = MemberLevel.query.filter(MemberLevel.levelName == m_args['levelName']).all()
        id_args = MemberLevel.query.filter(MemberLevel.id == id).all()[0]
        if args and m_args['levelName'] != id_args.levelName:
            return {'success': False, 'errorMsg': '会员等级已存在'}, 400
        del m_args['page']
        del m_args['pageSize']
        m_res = MemberLevel().update(id,**m_args)
        return {'success': True}, 201 
    
    def delete(self, id):
        response = MemberlevelSimpleAPI().get(id)['data']
        # if not response[0]['sysonline'] and not response[1]['bank'] and not response[2]:
        if not response[2]:
            m_res = MemberLevel().delete(id)
            return {'success': True}, 201
        else:
            return {'success': False,'errorMsg':'此等级下有会员还有代理不可以删除'}, 201
        # m_res = MemberLevel().delete(id)



class MemberlevelSimpleAPI(Resource):
    def get(self, id):
        sysonline = SysadminOnline().getdate(id)
        bank = SystemBankAccount().getdate(id)
        # len_sysonline = Member().getLen(id)[0][0][0]
        len_sysonline = Member().getLen(id)[0]
        len_sysonline = dict(len_sysonline)
        sysonline = dict(sysonline[0])
        bank = dict(bank[0])
        result_sysonline = []
        sysonline_args = {}
        result_bank = []
        bank_args = {}
        result_numbers = []
        numbers_args = {}
        for key, values in sysonline.items():
            result_one = {}
            result_one['id'] = key
            result_one['names'] = values
            result_sysonline.append(result_one)
        sysonline_args['sysonline'] = result_sysonline
        for key, values in bank.items():
            result_one = {}
            result_one['id'] = key
            result_one['names'] = values
            result_bank.append(result_one)
        bank_args['bank'] = result_bank
        keys = []
        result_one = {}
        for key, values in len_sysonline.items():
            keys.append(key)
            if 1 not in keys:
                result_one['numbers1'] = 0
                result_numbers.append(result_one)
            if 0 not in keys:
                result_one['numbers0'] = 0
                result_numbers.append(result_one)
            if 9 not in keys:
                result_one['numbers9'] = 0
                result_numbers.append(result_one)
            if 10 not in keys:
                result_one['numbers10'] = 0
                result_numbers.append(result_one)
            if 11 not in keys:
                result_one['numbers11'] = 0
                result_numbers.append(result_one)
            numbers = 'numbers{}'.format(key)
            result_one[numbers] = values
        result = {
            "success": True,
            "data": [sysonline_args, bank_args,result_one]
        }
        return result


class MemberlevelAllAPI(Resource):
    def get(self):
        result = []
        len_sysonline = Member().getAll()[0]
        len_sysonline = dict(len_sysonline)
        for keys,values in len_sysonline.items():
            args = {}
            args['id'] = keys
            args['numbers'] = values
            result.append(args)
        results = {
            "success": True,
            "data": result
        }
        return results


    
