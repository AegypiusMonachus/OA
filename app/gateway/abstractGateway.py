from ..models.member_account_change import Deposit,MemberAccountChangeRecord
from ..models.member import Member
from ..models import db
import json,hashlib,time
import traceback
import requests
from flask import current_app
from flask import g
from app.log import paylogger


class AbstractGateway:
    context = None
    amount = None
    username = None
    orderid = None
    porderid = None
    free = None
    def __init__(self):pass
    def before(self):pass
    def after(self):pass
    
    def setContext(self,m_context):
        self.context = m_context;
    def toPay(self):pass
    def synchor(self):pass
    def makeResponse(self):
        return 'SUCCESS'
    def notify(self):
        #接受参数
        parser = self.getNotifyRequestParameter()
        paylogger.info("异步通知传入参数%s"%(parser))
        #验证参数
        success = self.validate(parser)
        if success:
#             self.updateRecharge()
            self.accountChange(100004,0,None)
        else:
            self.accountChange(100004,99,"支付失败")
    
    def validate(self,parser):pass
        
    
    def getRequestParameter(self):pass
    
    #获取同步或者异步返回时的数据
    def getNotifyRequestParameter(self):pass
        
    def getSign(self,str,orderid,hasSign):
        key = None
        md = hashlib.md5()
        m_sql = '''select secret_key from blast_sysadmin_online where id = 
            (select mBankId from blast_member_recharge where rechargeId = %s)'''%(orderid)
        if hasSign:
            key = db.session.execute(m_sql).first()
            md.update((str + key.secret_key).encode())
        else:
            md.update((str).encode())
        return md.hexdigest()
    def getRechargeByOrderId(self,orderid):
        m_res = Deposit.query.filter(Deposit.number == orderid).first()
        return m_res
            
    def updateRecharge(self):
        try:
            m_res = Deposit.query.filter(Deposit.number == self.orderid).update({"pOrderid":self.porderid})
            db.session.commit()
        except Exception:
            traceback.print_exc()
            db.session.rollback()
 
    def accountChange(self,type,errorType,errorMsg):
        #获取入款信息
        deposit = self.getRechargeByOrderId(self.orderid)
        if self.amount is None:
            self.amount = deposit.applicationAmount
        errorType = errorType
        errorMsg = errorMsg
        if deposit.status != 1:
            return False
        if errorType == 0:
            if deposit.applicationAmount != self.amount:
                errorType = 99
                paylogger.info('%s 充值金额错误'%(self.orderid))
                # return {'messages': '%s 充值金额错误'%(self.orderid), 'success': False}
            if deposit.status != 1:
                errorType = 98
                paylogger.info('%s 状态错误'%(self.orderid))
                return False

        if errorType == 99:
            #更新入款表
            msql = '''update blast_member_recharge set 
                    state = 99,rechargeTime = %s,msg='%s' 
                    where rechargeId = %s and type =%s 
                    '''%(int(time.time()),errorMsg,self.orderid,type)
            db.session.execute(msql)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                db.session.remove()
            # return {'messages': '%s 状态错误' % (self.orderid), 'success': False}
            return False
        paylogger.info("会员%s入款%s 入款类型%s"%(deposit.username,self.amount,type))
        #获取用户账户信息
        member = Member.query.filter(Member.username == deposit.username).first();
        #根据用户获取优惠策略
        m_sql = '''select %s yh,ckjhb from blast_member_level where id = 
                    (select grade from blast_members where username = "%s")
                '''
        if type == 100004:
            m_sql = m_sql%("xszfyh",deposit.username)
        elif type == 100003:
            m_sql = m_sql%("gsrkyh",deposit.username)
        m_res = db.session.execute(m_sql).first()
        # 根据存款金额在优惠方案集合中找到最优的一个
        # if 'yh' in m_res:
        if m_res.yh and m_res.yh is not None:
            yh = self.findckyh(self.amount, json.loads(m_res.yh))
        else:
            yh = None
        paylogger.info("会员%s入款%s 优惠策略%s"%(deposit.username,self.amount,yh))
        #初始化各种优惠项
        yh_jhbs = 1.0;#稽核倍数
        yh_yhbl = 0;#优惠比例
        yh_yhsx = 0#优惠上线
        yh_ckje = 0#存款金额
        if yh:
            if 'yhsx' in yh and yh['yhsx'] is not '' or "" or None:
                yh_yhsx = yh['yhsx']
            if 'ckje' in yh and yh['ckje'] is not '' or "" or None:
                yh_ckje = yh['ckje']
            if 'jhbs' in yh and yh['jhbs'] is not '' or "" or None:
                yh_jhbs = float(yh['jhbs'])
            if 'yhbl' in yh and yh['yhbl'] is not '' or "" or None:
                yh_yhbl = float(yh['yhbl'])
        jh = None;
        if m_res.ckjhb:
            jh = json.loads(m_res.ckjhb)
        ckjh = 1.0
        if type == 100004:
            if 'xszf'in jh and jh['xszf']:
                ckjh = float(jh['xszf'])
        elif type == 100003:
            if 'gsrk'in jh and jh['gsrk']:
                ckjh = float(jh['gsrk'])
        else:
            if 'dkzf'in jh and  jh['dkzf']:
                ckjh = float(jh['dkzf'])
        #入款稽核
        jh = self.amount * ckjh
        #优惠计算
        yh_amount = self.amount * yh_yhbl;
        #判断优惠上线
        if yh:
            if 'yhsx' in yh and yh['yhsx']:
                yh_yhsx = float(yh['yhsx'])
                if yh_amount > yh_yhsx:
                    yh_amount = yh_yhsx;
        #优惠稽核
        yh_jh = yh_amount * yh_jhbs
        # m_args['uid'] = g.current_user.id
        #更新入款表
        userid = None
        porderid = self.porderid
        if hasattr(g, 'current_user'):
            userid = g.current_user.id
            msql = '''update blast_member_recharge set state = 2,rechargeTime = %s,rechargeAmount = %s,coin = %s,auditTime=%s, auditUser = %s ,p_orderid=%s  where rechargeId = %s and type =%s 
            '''%(int(time.time()),self.amount,member.balance,int(time.time()),userid,porderid,self.orderid,type)
        else:
            msql = '''update blast_member_recharge set state = 2,rechargeTime = %s,rechargeAmount = %s,coin = %s,auditTime=%s,p_orderid=%s  where rechargeId = %s and type =%s 
            '''%(int(time.time()),self.amount,member.balance,int(time.time()),porderid,self.orderid,type)
        db.session.execute(msql)
        paylogger.info("会员%s入款%s,入款稽核%s"%(deposit.username,self.amount,jh))
        paylogger.info("会员%s入款%s,优惠金额%s"%(deposit.username,self.amount,yh_amount))
        paylogger.info("会员%s入款%s,优惠稽核%s"%(deposit.username,self.amount,yh_jh))
        #更新用户余额
        msql = '''update blast_members set coin = coin + %s ,yhje = yhje + %s where username = "%s"
            '''%(self.amount + yh_amount,yh_amount,member.username)
        db.session.execute(msql)
        #添加账变
        coinLog = MemberAccountChangeRecord()
        coinLog.memberId = member.id
        coinLog.memberFrozenBalance = 0
        coinLog.amount = self.amount
        coinLog.memberBalance = member.balance + self.amount
        if type == 100003:
            coinLog.accountChangeType = 100001
            coinLog.info = '公司入款'
        elif type == 100004:
            coinLog.accountChangeType = 100002
            coinLog.info = '线上支付'
        coinLog.time = int(time.time());
        coinLog.actionUID = userid;
        coinLog.host = deposit.applicationHost
        coinLog.orderId = self.orderid
        coinLog.rechargeid = self.orderid
        coinLog.auditCharge = jh
        coinLog.auditType = 2
        coinLog.isAcdemen = 1
        db.session.add(coinLog)
        if yh_amount > 0:
            coinLog = MemberAccountChangeRecord()
            coinLog.memberId = member.id
            coinLog.memberFrozenBalance = 0
            coinLog.amount = yh_amount
            coinLog.memberBalance = member.balance +self.amount + yh_amount
            if type == 100003:
                coinLog.accountChangeType = 100010
                coinLog.info = '公司入款优惠'
            elif type == 100004:
                coinLog.accountChangeType = 100011
                coinLog.info = '线上支付优惠'
            coinLog.time = int(time.time());
            coinLog.actionUID = userid;
            coinLog.host = deposit.applicationHost
            coinLog.orderId = self.orderid
            coinLog.rechargeid = self.orderid
            coinLog.auditCharge = yh_jh
            coinLog.auditType = 3
            db.session.add(coinLog)
        #累计账户金额
        if type == 100003:
            msql = '''update blast_sysadmin_bank set amount = amount + %s where id = %s
                '''%(self.amount,deposit.systemBankAccountId)
        elif type == 100004:
            msql = '''update blast_sysadmin_online set amount = amount + %s where id = %s
                '''%(self.amount,deposit.systemBankAccountId)

        db.session.execute(msql)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            db.session.remove()
            return False
        paylogger.info("会员%s入款%s 金额增加完成"%(deposit.username,self.amount))
        return True
    '''
    根据存款金额找出对应的优惠方案
    '''        
    def findckyh(self,amount,yhList):
        yhjeDict={}
        yhLists = []
        #根据存款金额进行排序
        for args in yhList:
            m_parm = {key: args[key] for key in args if args[key] is not ''}
            if 'ckje' not in m_parm:
                m_parm['ckje'] = 0
            if m_parm:
                yhLists.append(m_parm)

        yhLists.sort(key = lambda x:float(x["ckje"]))
        for m_json in yhLists:
            if 'ckje' in m_json and m_json['ckje']:
                m_ckje = float(m_json['ckje'])
                yhjeDict = m_json
                #找出最相近优惠对象
                if m_ckje >= amount:
                    break
        return yhjeDict;
    
    '''
    根据系统的支付类型找到支付网关的支付类型
    '''
    def findPayType(self,dataMap):
        m_relation =  json.loads(dataMap['pay_type_relation'])
        pay_type = dataMap['pay_type']
        if pay_type !=1007:
            pay_type = m_relation[str(pay_type)]
        else:
            pay_type = dataMap['bank_type']
        return pay_type
        
        
    def createErrorHtml(self,errorMsg):
        m_html = ''' <body> <a>支付错误：%s</a> </body> '''%(errorMsg)
        return m_html
    
    def doPost(self,url,data,headers):
        paylogger.info("请求地址:%s,请求参数:%s"%(url,data))
        response  = requests.post(url,data = data,headers = headers)
        return response

    def doGet(self,url,data,headers):
        paylogger.info("请求地址:%s,请求参数:%s"%(url,data))
        response  = requests.get(url,params = data,headers = headers)
        return response

