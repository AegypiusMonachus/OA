from app.models.entertainment_city import EntertainmentCity
import requests,hashlib,json
from app.common.utils import strToBase64str
from app.common.orderUtils import createECOrderId
from flask import current_app
class AbstractEntertainmentCity:
    def __init__(self,ecCode):
        dao = EntertainmentCity().getDataByCode(ecCode)
        self.context = dao
               
    def register(self):    
        m_str = self.createRegisterStr()
        m_data = self.sign(m_str)
        m_headers = {'Content-Type':'text/plain'}
        m_url = self.context['apidomain'] + self.registerURL
        m_response = self.doPost(m_url, m_data, m_headers)
        return self.validateAndReturn(m_response,3002,"娱乐城登记失败")
    
    ''' 登录 '''
    def login(self,kargs):
        #self.register(kargs);
        #Transfer.withdrawalToAccount(self,kargs)
        m_str = self.createLoginStr(kargs)
        m_data = self.sign(m_str)
        m_headers = {'Content-Type':'text/plain'}
        m_url = self.context['apidomain'] + self.loginURL
        m_response = self.doPost(m_url, m_data, m_headers)
        return self.validateAndReturn(m_response,3002,"娱乐城登录失败")
    
    ''' 余额 '''
    def balance(self,kargs):
        m_str = self.createBalanceStr(kargs)
        m_data = self.sign(m_str)
        m_headers = {'Content-Type':'text/plain'}
        m_url = self.context['apidomain'] + self.balanceURL
        m_response = self.doPost(m_url, m_data, m_headers)
        return self.validateAndReturn(m_response,3002,"查询余额失败")

    '''更新钱包'''
    def updatebalance(self, kargs):
        m_str = self.updateBalanceStr(kargs)
        m_data = self.sign(m_str)
        m_headers = {'Content-Type': 'text/plain'}
        m_url = self.context['apidomain'] + self.balanceURL
        m_response = self.doPost(m_url, m_data, m_headers)
        return m_response
    ''' 存款 '''
    def deposit(self):
        #self.context['orderid'] = createECOrderId(self.context["member"].id)
        m_str = self.createDepositStr()
        m_data = self.sign(m_str)
        m_headers = {'Content-Type':'text/plain'}
        m_url = self.context['apidomain'] + self.depositURL
        m_response = self.doPost(m_url, m_data, m_headers)
        return self.validateAndReturn(m_response,3002,"存款失败")
    
    ''' 取款 '''
    def withdrawal(self,kargs):
        #self.context['orderid'] = createECOrderId(self.context["member"].id)
        m_str = self.createWithdrawalStr(kargs)
        m_data = self.sign(m_str)
        m_headers = {'Content-Type':'text/plain'}
        m_url = self.context['apidomain'] + self.withdrawalURL
        m_response = self.doPost(m_url, m_data, m_headers)
        return self.validateAndReturn(m_response,3002,"取款失败")

    ''' 取回钱包'''

    def getbalance(self, name,amount):
        # self.context['orderid'] = createECOrderId(self.context["member"].id)
        m_str = self.getbalanceStr(name,amount)
        m_data = self.sign(m_str)
        m_headers = {'Content-Type': 'text/plain'}
        m_url = self.context['apidomain'] + self.withdrawalURL
        m_response = self.doPost(m_url, m_data, m_headers)
        return m_response
    
    ''' 查询转账 '''
    def checkTransfer(self,kargs):
        #self.context['orderid'] = createECOrderId(self.context["member"].id)
        m_str = self.createCheckTransferStr(kargs)
        m_data = self.sign(m_str)
        m_headers = {'Content-Type':'text/plain'}
        m_url = self.context['apidomain'] + self.checkTransferURL
        m_response = self.doPost(m_url, m_data, m_headers)
        return self.validateAndReturn(m_response,3002,"查询转账失败")

    ''' 投注记录 '''
    def betRecord(self,kargs):
        #self.context['orderid'] = createECOrderId(self.context["member"].id)
        m_str = self.createBetRecordStr(kargs)
        print("同步投注记录%s"%(m_str))
        m_data = self.sign(m_str)
        m_headers = {'Content-Type':'text/plain'}
        m_url = self.context['apidomain'] + self.betRecordURL
        m_response = self.doPost(m_url, m_data, m_headers)
        return m_response



    ''' 游戏列表 '''
    def gameList(self,type):pass
    def getbalanceStr(self,name,amount):pass
    def createLoginStr(self,kargs):pass
    def createRegisterStr(self):pass
    def createBalanceStr(self,kargs):pass
    def updateBalanceStr(self,kargs):pass
    def createDepositStr(self,kargs):pass
    def createWithdrawalStr(self,kargs):pass
    def createCheckTransferStr(self,kargs):pass
    def createBetRecordStr(self,kargs):pass
    def saveBetRecordsToDB(self,eccode,gameType,newRecords):pass
    
    def doPost(self,url,data,headers):
        current_app.logger.info("请求地址："+url)
        current_app.logger.info("请求参数："+data)
        response  = requests.post(url,data = data,headers = headers)
        return response

    def sign(self, m_str):
        #1：将参数转成bash64
        current_app.logger.info("b46前："+m_str)
        m_str = strToBase64str(m_str)
        current_app.logger.info("b46后："+m_str)
        m_md5 = hashlib.md5()
        #2：按规定生成md5
        m_key = self.context['hash'] + m_str;
        current_app.logger.info("MD5前："+m_key)
        m_md5.update(m_key.encode("utf-8"))
        m_data = m_str + "." + m_md5.hexdigest()
        return m_data

    '''验证api接口返回的数据是否正确，并返回数据'''
    def validateAndReturn(self,response,errorCode,errorMsg):
        m_data = None;
        if isinstance(response,str) == False:
            status_code = response.status_code
            if status_code >= 400:
                return {"success": False,'errorCode': 3000,'errorMsg': "请求错误"}
            m_data = response.text
        else:
            m_data = response
        if m_data is None:
            return {"success": False,'errorCode': 3000,'errorMsg': "没获取到数据"}
        #将字符串转换成json
        current_app.logger.info('返回参数：%s'%(m_data))
        m_json = json.loads(m_data)
        if m_json['Success']:
            if m_json.__contains__('Data'):
                return {"success": True,"data" : m_json['Data']}
        else:
            return {"success": False,'errorCode': errorCode,'errorMsg': errorMsg}

            
        
        
        
            
            
            
            
            
    