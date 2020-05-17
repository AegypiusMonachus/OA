import time,hashlib
from app.common.utils import strToBase64str
from app.entertainmentcity.abstractEntertainmentCity import AbstractEntertainmentCity
from app.models.member import Member
from flask import current_app
'''
    KK 自主运营的娱乐城
'''

class KKEntertainmentCity(AbstractEntertainmentCity):
    def __init__(self,ecCode):
        self.context = {}
    
    ''' 余额 '''
    def balance(self,kargs):
        if 'member' not in self.context:
            return self.validateAndReturn(None,3002,"查询余额失败，用户未登录")
        member = self.context['member']
        balance = Member.query.filter(Member.username == member.username).with_entities(Member.balance).scalar()
        return {"success": True,"data" : {'balance':balance}}

    ''' 更新钱包 '''
    def updateBalanceStr(self,kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","timestamp":"%s"}'''%(self.context['merchantCode'],kargs,int(time.time()))
        return m_str;

    ''' 存款 '''
    def deposit(self):
        if 'member' not in self.context:
            return self.validateAndReturn(None,3002,"存款余额失败，用户未登录")
        member = self.context['member']
        amount = self.context['amount']
        last_ce = self.context['last_ce']
        try:
            new_Member = Member.amountToMemberAccount(member.username, amount)
        except Exception as e:
            current_app.logger.exception(e)
            current_app.logger.error("%s向主账户存款失败，内部错误%s"%(member.username,e))
            current_app.logger.error("%s从%s娱乐城取款%s已经完成，但是将金额存回主账户时错误,请查看详细日志。"%(member.username,self.context['last_ce'],amount))
            current_app.logger.error({"success": False,'errorCode': 9001,'errorMsg': "%s从%s娱乐城取款%s已经完成，但是将金额存回主账户时错误,这是一个严重错误,需要人工存入"}%(member.username,self.context['last_ce'],amount))
            return {"success": False,'errorCode': 3001,'errorMsg': "转账失败"} 
        
    
    
    
    
    
    
    '''验证api接口返回的数据是否正确，并返回数据'''
    def validateAndReturn(self,response,errorCode,errorMsg):
        return {"success": False,'errorCode': errorCode,'errorMsg': errorMsg}
