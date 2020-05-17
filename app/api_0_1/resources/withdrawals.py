'''
Created on 2019年1月6日

@author: liuyu
'''
from flask import request, g,current_app
from flask_restful import Resource, marshal_with, fields, abort
from sqlalchemy.sql import func
from app.models.member import Member
from app.models.member_level import MemberLevel
from app.models.bank_account import MemberBankAccount
from app.models.blast_bets import BlastBets
from app.models.member_account_change import Withdrawal, MemberAccountChangeRecord
from app.models import db
import uuid,time
from flask_restful.reqparse import RequestParser
from app.common.utils import *
from ..common import *
from ..common.utils import *
import hashlib
import requests
from app.common.orderUtils import *
from app.models.memeber_history import *
from app.models.audits import Audits


'''
取款申請
'''
class Qksq(Resource):
    from app.auth.common import token_auth
    decorators = [token_auth.login_required]
    def post(self):
        parser = RequestParser(trim=True)
        parser.add_argument('amount', type=float, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('memberBankId', type=int, required=True)
        args = parser.parse_args(strict=True)
        if not hasattr(g, 'current_member'):
            return {
            'errorCode': 9999,
            'errorMsg': "用戶未登录",
            'success': False
            }

        uid = g.current_member.id;
        print("%s用户取款申请"%(uid))
        qkamount = args['amount'];
        qktime = int(time.time())
        pwd = args['password']
        member = Member.query.filter(Member.id == uid).first()
        status = member.status

        if status == 2:
            return {
                'errorCode': 1101,
                'errorMsg': "该用户已被冻结",
                'success': False
            }
        if status == 0:
            return {
                'errorCode': 1101,
                'errorMsg': "该用户已被禁用",
                'success': False
            }
        if pwd != member.fundPasswordHash:
            return {
                'errorCode': 1101,
                'errorMsg': "密码错误",
                'success': False
            }
        levelId = member.levelConfig
        levelMinAmount = db.session.query(MemberLevel.min_tk,MemberLevel.max_tk).filter(MemberLevel.id == levelId).all()
        if levelMinAmount:
            min_amount = levelMinAmount[0][0]
            max_amount = levelMinAmount[0][1]
            if min_amount:
                if args['amount'] <= min_amount:
                    return {
                        'errorCode': 1101,
                        'errorMsg': "取款金额不能小于会员等级最小金额",
                        'success': False
                    }
            if max_amount:
                if args['amount'] >= max_amount:
                    return {
                        'errorCode': 1101,
                        'errorMsg': "取款金额不能大于会员等级最大金额",
                        'success': False
                    }
        memberBank = MemberBankAccount.query.filter(MemberBankAccount.id == args['memberBankId'],MemberBankAccount.memberId == uid).first()
        m_return = getAllCost(uid,member)
        m_sxf = m_return['sxf']
        m_xzf = m_return['xzf']
        m_yjkc= m_return['yhkc']
        m_qksxf = m_sxf + m_xzf + m_yjkc
        m_ye = member.balance - m_qksxf - qkamount
        if m_ye >= 0:
            m_orderid = self.updateInfo(member, memberBank, qkamount, qktime, m_sxf, m_xzf, m_yjkc)
        else:
            return {"success":False,"errorCode":1101,"errorMsg":"取款费用大于账户余额"}
        return {"success":True};

    '''更新数据'''            
    def updateInfo(self,member,memberBank,qkamount,qktime,sxf,xzf,yhkc):
        #添加出款信息
        withdrawal = Withdrawal()
        withdrawal.status = 1
        withdrawal.type = 200001
        withdrawal.applicationAmount = qkamount+sxf+xzf+yhkc
        withdrawal.applicationTime = qktime
        withdrawal.applicationHost = host_to_value(request.remote_addr)
        withdrawal.memberId = member.id
        withdrawal.bankId = memberBank.bankId
        withdrawal.bankAccountNumber = memberBank.accountNumber
        withdrawal.bankAccountName = memberBank.accountName
        withdrawal.withdrawalAmount = qkamount
        withdrawal.sxf = sxf
        withdrawal.yhkc = yhkc
        withdrawal.xzf = xzf
        uid = g.current_member.id
        withdrawal.orderID = createOrderIdNew(uid=uid)
        # 提现申请时，更新会员余额
        # 提现申请时，更新会员冻结余额
        if member.balance is None:
            member.balance = 0
        if withdrawal.withdrawalAmount is None:
            withdrawal.withdrawalAmount = 0
        if member.frozenBalance is None:
            member.frozenBalance = 0
        member.balance -= withdrawal.applicationAmount
        member.frozenBalance += withdrawal.applicationAmount
        try:
            db.session.add(member)
            db.session.add(withdrawal)
            db.session.commit()
            #添加提款信息
            member_account_change_record = MemberAccountChangeRecord()
            member_account_change_record.memberId = member.id
            member_account_change_record.memberBalance = member.balance
            member_account_change_record.memberFrozenBalance = member.frozenBalance
            member_account_change_record.amount = -withdrawal.withdrawalAmount
            member_account_change_record.sxf = -(sxf+xzf+yhkc)
            member_account_change_record.accountChangeType = 200001
            member_account_change_record.time = withdrawal.applicationTime
            member_account_change_record.host = withdrawal.applicationHost  
            member_account_change_record.rechargeid = withdrawal.orderID
            member_account_change_record.orderId = withdrawal.orderID
            try:
                db.session.add(member_account_change_record)
                db.session.commit()
                OperationHistory().PublicMeDatasApplyGet(200001,withdrawal)
            except:
                db.session.rollback()
                db.session.remove()
                abort(500)

            try:
                requests.request('GET', 'http://127.0.0.1:8125/main/memberWithdrawal', timeout=1)
            except:
                pass   
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return withdrawal.orderID;
    
class CheckDML(Resource):
    from app.auth.common import token_auth
    decorators = [token_auth.login_required]
    def get(self):
        if not hasattr(g, 'current_member'):
            abort(http_status_code=500, **{
                'errorCode': 9999,
                'errorMsg': "用戶未登录",
                'success': False
            })
        uid = g.current_member.id;
        current_app.logger.info("%s用户取款检查当前稽核"%(uid))
        member= Member.query.filter(Member.id == uid).first()
        m_return = getAllCost(uid,member)
        return {"success":True,"data":m_return}

'''计算所有费用'''
def getAllCost(uid,member):
    m_sql_level = ''' select min_tk,max_tk,sx_Free,xz_Free,js,mcfy,tksc,ms from blast_member_level 
            where id = (select grade from blast_members where uid = %s)'''%(uid)
    m_level = db.session.execute(m_sql_level).first()
    m_audit = Audits().audits(uid)
    m_sxf = 0
    m_xzf = 0
    m_yhkc = 0
    m_return = {'min_tk':m_level['min_tk'],'max_tk':m_level['max_tk']}
    if m_audit == None:
        m_return['sxf'] = m_sxf
        m_return['xzf'] = m_xzf
        m_return['yhkc'] =m_yhkc
    else:
        m_yhkc = m_audit['failed_yh_amount']
        m_xzf = m_audit['failed_deposit_amount']
        m_deposit_pass = m_audit['deposit_pass']
        '''如果存款稽核没有达到，始终收取手续费'''
        if m_deposit_pass == False:
            m_sxf = m_level['sx_Free']
        else:
            m_sxf = getSxf(m_level, int(time.time()))
    m_sxf = m_sxf if m_sxf else 0
    m_return['sxf'] = m_sxf
    m_return['xzf'] = m_xzf
    m_return['yhkc'] = m_yhkc
    return m_return

'''计算手续费'''
def getSxf(level,qktime):
    m_sxf = level.sx_Free if level.sx_Free else 0
    if level.mcfy == 1:
        return 0;
    if level.js == 1:
        return m_sxf
    #计算提款次数
    m_limit = level.tksc
    if m_limit is None:
        m_limit = 0
    lasttime = qktime - m_limit*3600
    tkcs = db.session.query(func.count(Withdrawal.id)).filter(Withdrawal.applicationTime>=lasttime,Withdrawal.applicationTime<=qktime).scalar()
    tkcs = tkcs + 1;
    if level.ms is None:
        level.ms = 0
    if tkcs > level.ms:
        return m_sxf
    else:
        return 0;
