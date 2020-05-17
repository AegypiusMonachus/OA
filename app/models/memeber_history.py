import random

from sqlalchemy.sql import func

from app.models.common.utils import *
from app.common.utils import *
from . import db
from flask import request, g, current_app
from app.models.user import User
from app.models.member import Member

class OperationHistory(db.Model):
    __tablename__ = 'blast_operation_history'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    auditime = db.Column(db.Integer)
    info = db.Column(db.String, default=None)
    makeUser = db.Column(db.String, default=None)
    orderId = db.Column(db.String)
    contents = db.Column(db.String, default=None)
    ip = db.Column(db.String, default=None)
    amount = db.Column(db.Float, default=None)
    username = db.Column(db.String,default=None)
    makeUserName= db.Column(db.String,default=None)
    types = db.Column(db.Integer)

    def getdata(self,criterion):
        args = db.session.query(OperationHistory).filter(*criterion).order_by(OperationHistory.auditime.desc()).all()
        return args

    def insert(self, **kwargs):
        dao = OperationHistory(**kwargs)
        try:
            db.session.add(dao)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
        return True


    def memberHistory(self,args):
        m_res = OperationHistory().insert(**args)


    def memberUser(self,uid):
        deposit = db.session.query(User.username).filter(User.id == uid).first()[0]
        return deposit

    def getMember(self,uid):
        deposit = db.session.query(Member.username).filter(Member.id == uid).first()[0]
        return deposit
    def getMemberAll(self,uid):
        deposit = Member.query.filter(Member.id == uid).first()
        print(deposit)
        return deposit


    def PublicData(self,types,deposit):
        m_args = {}
        m_args['uid'] = deposit.memberId
        m_args['auditime'] = deposit.applicationTime
        if types == 100003:
            m_args['info'] = '公司入款-确认'
            m_args['types'] = 100003
        if types == 100004:
            m_args['info'] = '线上支付-确认'
            m_args['types'] = 100004
        if types == 900001:
            m_args['info'] = '人工存入-后台提存'
            m_args['types'] = 100005
        if types == 900002:
            m_args['info'] = '人工存入-优惠活动'
            m_args['types'] = 100005
        if types == 900003:
            m_args['info'] = '人工存入-补发派奖'
            m_args['types'] = 100005
        if types == 900004:
            m_args['info'] = '人工存入-反水'
            m_args['types'] = 100005
        if types == 900005:
            m_args['info'] = '人工存入-其他'
            m_args['types'] = 100005
        if hasattr(g, 'current_user'):
            m_args['makeUserName'] = self.memberUser(g.current_user.id)
            m_args['makeUser'] = g.current_user.id
        else:
            m_args['makeUserName'] = None
            m_args['makeUser'] = None
        m_args['orderId'] = deposit.number
        m_args['contents'] = None
        m_args['ip'] = host_to_value(request.remote_addr)
        m_args['amount'] = deposit.applicationAmount
        m_args['username'] = deposit.username
        self.memberHistory(m_args)

    def PublicDatas(self,types,withdrawal):
        m_args = {}
        m_args['uid'] = withdrawal.memberId
        m_args['auditime'] = withdrawal.applicationTime
        if types == 900001:
            m_args['info'] = '人工提出-后台提存'
            m_args['types'] = 100005
        if types == 900002:
            m_args['info'] = '人工提出-优惠活动'
            m_args['types'] = 100005
        if types == 900003:
            m_args['info'] = '人工提出-补发派奖'
            m_args['types'] = 100005
        if types == 900004:
            m_args['info'] = '人工提出-反水'
            m_args['types'] = 100005
        if types == 900005:
            m_args['info'] = '人工提出-其他'
            m_args['types'] = 100005
        if types == 200002:
            m_args['info'] = '取款申请审核-确认取款'
            m_args['types'] = 100006
        if types == 200003:
            m_args['info'] = '在线取款-退回'
            m_args['types'] = 100006
        if types == 200004:
            m_args['info'] = '在线取款-拒绝'
            m_args['types'] = 100006
        m_args['makeUserName'] = self.memberUser(g.current_user.id)
        m_args['makeUser'] = g.current_user.id
        m_args['orderId'] = withdrawal.orderID
        m_args['contents'] = None
        m_args['ip'] = host_to_value(request.remote_addr)
        m_args['amount'] = withdrawal.applicationAmount
        m_args['username'] = self.getMember(withdrawal.memberId)
        self.memberHistory(m_args)

    def PublicMeDatas(self,types,memberId):
        m_args = {}
        m_args['uid'] = memberId
        m_args['auditime'] = int(time.time())
        if types == 1111:
            m_args['info'] = '修改银行账户信息'
        if types == 2222:
            m_args['info'] = '修改个人基本信息'
        if types == 900003:
            m_args['info'] = '人工提出-补发派奖'
        if types == 900004:
            m_args['info'] = '人工提出-反水'
            m_args['types'] = 100005
        if types == 900005:
            m_args['info'] = '人工提出-其他'
            m_args['types'] = 100005
        m_args['contents'] = None
        m_args['ip'] = host_to_value(request.remote_addr)
        m_args['username'] = self.getMember(memberId)
        m_args['makeUserName'] = self.memberUser(g.current_user.id)
        m_args['makeUser'] = g.current_user.id
        self.memberHistory(m_args)

    def PublicMeDatasApply(self, types, deposit):
        m_args = {}
        m_args['uid'] = deposit.memberId
        m_args['auditime'] = deposit.applicationTime
        if types == 100003:
            m_args['info'] = '公司入款-申请'
            m_args['types'] = 100003
        if types == 100004:
            m_args['info'] = '线上支付-申请'
            m_args['types'] = 100004


        m_args['orderId'] = deposit.number
        m_args['contents'] = None
        m_args['ip'] = host_to_value(request.remote_addr)
        m_args['amount'] = deposit.applicationAmount
        m_args['username'] = deposit.username
        m_args['makeUserName'] = deposit.username
        self.memberHistory(m_args)

    def PublicMeDatasApplyGet(self, types, withdrawal):
        m_args = {}
        m_args['uid'] = withdrawal.memberId
        m_args['auditime'] = withdrawal.applicationTime
        if types == 200001:
            m_args['info'] = '取款申请审核-申请'
            m_args['types'] = 100006

        m_args['orderId'] = withdrawal.orderID
        m_args['contents'] = None
        m_args['ip'] = host_to_value(request.remote_addr)
        m_args['amount'] = withdrawal.applicationAmount
        m_args['username'] = self.getMember(withdrawal.memberId)
        m_args['makeUserName'] = self.getMember(withdrawal.memberId)
        self.memberHistory(m_args)

    def PublicMemberDatasApply(self, types, memberId):
        m_args = {}
        m_args['uid'] = memberId
        m_args['auditime'] = int(time.time())
        if types == 1001:
                m_args['info'] = '创建一个新的会员'
        if types == 1002:
            m_args['info'] = '创建一条基本资料'
        if types == 1003:
            m_args['info'] = '创建一条新的银行信息'
        if types == 2001:
            m_args['info'] = '创建一个新的代理'
        if types == 2002:
            m_args['info'] = '申请成为代理'
        m_args['contents'] = None
        m_args['makeUserName'] = self.memberUser(g.current_user.id)
        m_args['makeUser'] = g.current_user.id
        m_args['ip'] = host_to_value(request.remote_addr)
        m_args['username'] = self.getMember(memberId)
        self.memberHistory(m_args)

    def PublicAgensData(self,types,audit):
        m_args = {}
        m_args['uid'] = audit.memberId
        m_args['auditime'] = int(time.time())
        if types == 2003:
            m_args['info'] = '该代理申请审核通过'
        m_args['makeUserName'] = self.memberUser(g.current_user.id)
        m_args['makeUser'] = g.current_user.id
        m_args['orderId'] = None
        m_args['contents'] = None
        m_args['ip'] = host_to_value(request.remote_addr)
        m_args['amount'] = None
        m_args['username'] = self.getMember(audit.memberId)
        self.memberHistory(m_args)

    def PublicDatasAll(self,types,withdrawals):
        for withdrawal in withdrawals:
            m_args = {}
            m_args['uid'] = withdrawal.memberId
            m_args['auditime'] = withdrawal.applicationTime
            if types == 900002:
                m_args['info'] = '人工(提)'
                m_args['types'] = 100005
            if types == 900007:
                m_args['info'] = '人工(提)-优惠活动'
                m_args['types'] = 100005
            if types == 900008:
                m_args['info'] = '人工(提)-补发派奖'
                m_args['types'] = 100005
            if types == 900009:
                m_args['info'] = '人工(提)-返水'
                m_args['types'] = 100005
            if types == 900010:
                m_args['info'] = '人工(提)-其他'
                m_args['types'] = 100005
            if types == 200001:
                m_args['info'] = '取款申请审核-确认取款'
                m_args['types'] = 100006
            m_args['makeUserName'] = self.memberUser(g.current_user.id)
            m_args['makeUser'] = g.current_user.id
            m_args['orderId'] = withdrawal.orderID
            m_args['contents'] = None
            m_args['ip'] = host_to_value(request.remote_addr)
            m_args['amount'] = withdrawal.applicationAmount
            m_args['username'] = self.getMember(withdrawal.memberId)
            self.memberHistory(m_args)

    def PublicDataGo(self, types, deposits):
        for deposit in deposits:
            m_args = {}
            m_args['uid'] = deposit.memberId
            m_args['auditime'] = deposit.applicationTime
            if types == 900001:
                m_args['info'] = '人工(存)'
                m_args['types'] = 100005
            if types == 900003:
                m_args['info'] = '人工(存)-补发派奖'
                m_args['types'] = 100005
            if types == 900004:
                m_args['info'] = '人工(存)-返水'
                m_args['types'] = 100005
            if types == 900005:
                m_args['info'] = '人工(存)-其他'
                m_args['types'] = 100005
            if types == 900006:
                m_args['info'] = '人工(存)-优惠活动'
                m_args['types'] = 100005

            m_args['makeUserName'] = self.memberUser(g.current_user.id)
            m_args['makeUser'] = g.current_user.id
            m_args['orderId'] = deposit.number
            m_args['contents'] = None
            m_args['ip'] = host_to_value(request.remote_addr)
            m_args['amount'] = deposit.applicationAmount
            m_args['username'] = deposit.username
            self.memberHistory(m_args)

    def SysAndBank(self, types, name):
        m_args = {}
        if types == 300011:
            m_args['info'] = '新增线上支付商户'

        m_args['auditime'] = int(time.time())
        m_args['makeUserName'] = self.memberUser(g.current_user.id)
        m_args['makeUser'] = g.current_user.id

    def UserLogin(self, types, user):
        m_args = {}
        if types == 400001:
            m_args['info'] = '登陆IP'
        m_args['auditime'] = user.lastLoginTime
        m_args['ip'] = user.lastLoginIP
        m_args['makeUserName'] = self.memberUser(g.current_user.id)
        m_args['makeUser'] = g.current_user.id
        self.memberHistory(m_args)