'''
Created on 2019
娱乐城
@author: liuyu
'''
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask import g,current_app
from app.models.entertainment_city import EntertainmentCity
from app.auth.common import token_auth
from app.entertainmentcity import EntertainmentCityFactory
from app.entertainmentcity.amountTransfer import AmountTransfer
from flask import request
from app.common.utils import host_to_value 
from app.common.orderUtils import createECOrderId
#from app.common.EntertainmentCityThreadPool import EntertainmentCityThreadPool
import time

tempUser = ['xg123','xl123','she007','lc6666','cc000','cc111','jl123','jl234','hhco1','hhco4']

'''
娱乐城接口
'''
class EntertainmentCityAPI(Resource):
    decorators = [token_auth.login_required]
    def get(self, code=None):
        m_data = None
        if code:
            pass
        else:
            m_data = EntertainmentCity().getEC()
        return {"success": True,"data":m_data};
    
    '''登录一个娱乐城'''
    def post(self,code):
        if not hasattr(g, 'current_member'):
            return {'errorCode': "9999",'errorMsg': "用戶未登录",'success': False}
        parser = RequestParser(trim=True)
        parser.add_argument('deviceTypeCode', type=str)#  電腦版: PC, 手機版: Mobile
        parser.add_argument('gameCode', type=str)#游戏代码
        parser.add_argument('isDemo', type=str,default=0)#是否试玩，默认否
        kargs = parser.parse_args(strict=True)
        current_app.logger.info("%s用户登录%s娱乐城"%(g.current_member.username,code))
        if g.current_member.username not in tempUser:
            return {"success": False,'errorCode': 3000,'errorMsg': "没有权限"}
        try:
            mContext = {}
            mContext["member"] = g.current_member
            mContext["ip"] = host_to_value(request.remote_addr)
            mContext["real_ip"] = request.remote_addr
            mContext["loginEC"] = code#选择登录的娱乐城
            m_data = {'success':True}
            ce = EntertainmentCityFactory.getEntertainmentCity(code);
            if ce is None:
                current_app.logger.error({"success": False,'errorCode': 3000,'errorMsg': "没有中找到娱乐城"})
                return {"success": False,'errorCode': 3000,'errorMsg': "登录失败"}
            ce.context["member"] = g.current_member
            if code != 'MAIN':
                m_data = ce.register()
            if 'success' not in m_data or m_data['success'] == False:
                return {"success": False,'errorCode': 3000,'errorMsg': "登录失败"}
            if g.current_member.auto_change == 1:
                current_app.logger.info('---------额度转换开始------------')
                AmountTransfer.withdrawalToAccount(mContext,kargs)
                if code != 'MAIN':
                    AmountTransfer.accountToEntertainmentCity(mContext,kargs,ce)
                current_app.logger.info('---------额度转换结束------------')
            if code != 'MAIN':
                m_data = ce.login(kargs)
            if 'success' not in m_data or m_data['success'] == False:
                return {"success": False,'errorCode': 3000,'errorMsg': "登录失败"}
            AmountTransfer.saveECLog(g.current_member.id, g.current_member.username, int(time.time()), code, mContext['ip'])
        except RuntimeError as e:
            return {"success": False,'errorCode': 3000,'errorMsg': "登录失败"}
        return m_data
    
'''
余额查询接口
'''
class BalanceAPI(Resource):
    def post(self,code):
        if not hasattr(g, 'current_member'):
            return {'errorCode': "9999",'errorMsg': "用戶未登录",'success': False}
        if g.current_member.isTsetPLay == 1:
            return { 'errorCode': "3030",'errorMsg':"试玩用户不提供此功能", 'success': False}
        ce = EntertainmentCityFactory.getEntertainmentCity(code);
        ce.context["member"] = g.current_member
        m_data = ce.balance(None)
        return m_data
'''
存款接口
'''
class DepositAPI(Resource):
    def post(self,code):
        parser = RequestParser(trim=True)
        parser.add_argument('amount', type=float)
        kargs = parser.parse_args(strict=True)
        if not hasattr(g, 'current_member'):
            return {'errorCode': "9999",'errorMsg': "用戶未登录",'success': False}
        if g.current_member.isTsetPLay == 1:
            return { 'errorCode': "3030",'errorMsg':"试玩用户不提供此功能", 'success': False}
        ce = EntertainmentCityFactory.getEntertainmentCity(code);
        ce.context["member"] = g.current_member
        ce.context["orderid"] = createECOrderId(g.current_member.id)
        ce.context['amount'] = kargs['amount']
        m_data = ce.deposit()
        return m_data
    
'''
取款接口
'''
class WithdrawalAPI(Resource):
    def post(self,code):
        parser = RequestParser(trim=True)
        parser.add_argument('amount', type=float)
        kargs = parser.parse_args(strict=True)
        if not hasattr(g, 'current_member'):
            return {'errorCode': "9999",'errorMsg': "用戶未登录",'success': False}
        if g.current_member.isTsetPLay == 1:
            return { 'errorCode': "3030",'errorMsg':"试玩用户不提供此功能", 'success': False}
        ce = EntertainmentCityFactory.getEntertainmentCity(code);
        ce.context["member"] = g.current_member
        ce.context["orderid"] = createECOrderId(g.current_member.id)
        ce.context['amount'] = kargs['amount']
        m_data = ce.withdrawal(kargs)
        return m_data   
    
'''
登记接口
'''
class RegisterAPI(Resource):
    def post(self,code):
        parser = RequestParser(trim=True)
        parser.add_argument('isDemo', type=int)
        parser.add_argument('merchantCode', type=str)
        parser.add_argument('username', type=str)
        parser.add_argument('token', type=str)
        parser.add_argument('timestamp', type=str)
        kargs = parser.parse_args(strict=True)
        if not hasattr(g, 'current_member'):
            return {'errorCode': "9999",'errorMsg': "用戶未登录",'success': False}
#         if g.current_member.isTsetPLay == 1:
#             return { 'errorCode': "3030",'errorMsg':"试玩用户不提供此功能", 'success': False}
        ce = EntertainmentCityFactory.getEntertainmentCity(code);
        ce.context["member"] = g.current_member
        m_data = ce.register()
        return m_data
    
'''
登录接口
'''
class LoginAPI(Resource):
    def post(self,code):
        parser = RequestParser(trim=True)
        parser.add_argument('deviceTypeCode', type=str)#  電腦版: PC, 手機版: Mobile
        parser.add_argument('gameCode', type=str)#游戏代码
        parser.add_argument('isDemo', type=str,default=0)#是否试玩，默认否
        kargs = parser.parse_args(strict=True)
        if not hasattr(g, 'current_member'):
            return {'errorCode': "9999",'errorMsg': "用戶未登录",'success': False}
#         if g.current_member.isTsetPLay == 1:
#             return { 'errorCode': "3030",'errorMsg':"试玩用户不提供此功能", 'success': False}
        ce = EntertainmentCityFactory.getEntertainmentCity(code);
        ce.context["member"] = g.current_member
        m_data = ce.login(kargs)
        return m_data
'''
检查接口
'''
class CheckTransferAPI(Resource):
    def get(self,code):
        ce = EntertainmentCityFactory.getEntertainmentCity(code);
        kargs = None
        m_data = ce.checkTransfer(kargs)
        return m_data

'''
投注记录
'''
class BetRecordAPI(Resource):
    def get(self,code):
        if not hasattr(g, 'current_member'):
            return {'errorCode': "9999",'errorMsg': "用戶未登录",'success': False}
        if g.current_member.isTsetPLay == 1:
            return { 'errorCode': "3030",'errorMsg':"试玩用户不提供此功能", 'success': False}
        parser = RequestParser(trim=True)
        parser.add_argument('startDate', type=str)
        parser.add_argument('endDate', type=str)
        parser.add_argument('pageIndex', type=int)
        parser.add_argument('gameType', type=str)
        kargs = parser.parse_args(strict=True)
        ce = EntertainmentCityFactory.getEntertainmentCity(code);
        ce.context["member"] = g.current_member
        m_data = ce.betRecord(kargs)
        return m_data.text

'''
从一个娱乐城取款到另一个娱乐城
'''    
class ChangeAmountAPI(Resource):
    def post(self):
        if not hasattr(g, 'current_member'):
            return {'errorCode': "9999",'errorMsg': "用戶未登录",'success': False}
        parser = RequestParser(trim=True)
        parser.add_argument('fromEC', type=str,required=True)#源娱乐城
        parser.add_argument('toEC', type=str,required=True)#目标娱乐城
        parser.add_argument('amount', type=float,required=True)#金额
        parser.add_argument('isDemo', type=int,default=0)#金额
        kargs = parser.parse_args(strict=True)
        if g.current_member.username not in tempUser:
            return {"success": False,'errorCode': 3000,'errorMsg': "没有权限"}
        amount = kargs['amount']
        if amount < 1:
            return {"success": False,'errorCode': 3001,'errorMsg': "转账发生错误"}  
        fromEC = kargs['fromEC']
        toEC = kargs['toEC']
        mContext = {}
        mContext["member"] = g.current_member
        mContext["ip"] = host_to_value(request.remote_addr)
        mContext["real_ip"] = request.remote_addr
        mContext["loginEC"] = toEC#选择登录的娱乐城
        current_app.logger.info('---------%s从%s转账到%s 开始------------'%(g.current_member.username,fromEC,toEC))
        m_data = {'success':True}
        if fromEC =='MAIN':
            ce = EntertainmentCityFactory.getEntertainmentCity(toEC);
            ce.context["member"] = g.current_member
            ce.register()
            m_data = AmountTransfer.accountToEntertainmentCity(mContext,kargs,ce)
        elif toEC =='MAIN':
            m_data = AmountTransfer.withdrawalToAccount(mContext,kargs)
#         else:
#             m_data = AmountTransfer.withdrawalToAccount(mContext,kargs)
#             ce = EntertainmentCityFactory.getEntertainmentCity(toEC);
#             ce.context["member"] = g.current_member
#             m_data = AmountTransfer.accountToEntertainmentCity(mContext,kargs,ce)
        #AmountTransfer.saveECLog(g.current_member.id, g.current_member.username, int(time.time()), toEC, mContext['ip'])
        current_app.logger.info('---------%s从%s转账到%s 结束------------'%(g.current_member.username,fromEC,toEC))
        return m_data

'''
转账记录查询
'''
class SearachTransfer(Resource):
    def post(self,code):
        if not hasattr(g, 'current_member'):
            return {'errorCode': "9999",'errorMsg': "用戶未登录",'success': False}
        if g.current_member.isTsetPLay == 1:
            return { 'errorCode': "3030",'errorMsg':"试玩用户不提供此功能", 'success': False}
        parser = RequestParser(trim=True)
        parser.add_argument('merchantCode', type=str)
        parser.add_argument('merchantTransSN', type=str)
        # parser.add_argument('GameTransSN', type=str)
        parser.add_argument('timestamp', type=str)
        # parser.add_argument('username', type=str)
        kargs = parser.parse_args(strict=True)
        ce = EntertainmentCityFactory.getEntertainmentCity(code);
        ce.context["member"] = g.current_member
        m_data = ce.checkTransfer(kargs)
        return m_data