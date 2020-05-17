import json,time
import re

from flask import current_app

from app.entertainmentcity.abstractEntertainmentCity import AbstractEntertainmentCity
from app.models import db
from app.models.entertainment_city_bets_detail import EntertainmentCityBetsDetail

'''
    PT Entertainment City
'''
class PTEntertainmentCity(AbstractEntertainmentCity):
    
    gameListURL = '/API/PT/GetGameList'
    loginURL = '/API/PT/Login'
    balanceURL = '/API/PT/Balance'
    depositURL = '/API/PT/Deposit'
    withdrawalURL = '/API/PT/Withdrawal'
    betRecordURL = '/API/PT/BetRecord'
    registerURL = '/API/PT/Register'
    # withdrawalURL = '/API/PT/Withdrawal'
    '''获取游戏列表'''
    def gameList(self,type):
        if type == 1:
            m_data = self.getGameListByLocal()
        elif type == 2:
            m_data = self.getGameListByAPI()
        return self.validateAndReturn(m_data,3003,"获取游戏列表失败")
    
    ''' 登录 '''
    def createLoginStr(self,kargs):
        m_str = '''
                {"merchantCode":"%s","username":"%s","token":"%s",
                "extension":{"gameCode":"%s","deviceTypeCode":"%s",
                "languageCode":"%s"},"timestamp":"%s"}
                '''%(self.context['merchantCode'],self.context["member"].username,
                     self.context['token'],kargs['gameCode'],kargs['deviceTypeCode'],'zhCN',int(time.time()))
        return m_str;

    def createRegisterStr(self):
        m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","timestamp":"%s"}'''%(self.context['merchantCode'],self.context['member'].username,
                     self.context['token'],int(time.time()))
        return m_str;

    ''' 余额 '''
    def createBalanceStr(self,kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","timestamp":"%s"}'''%(self.context['merchantCode'],self.context["member"].username,int(time.time()))
        return m_str;

    ''' 更新钱包 '''
    def updateBalanceStr(self,kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","timestamp":"%s"}'''%(self.context['merchantCode'],kargs,int(time.time()))
        return m_str;

    ''' 存款 '''
    def createDepositStr(self):
        m_str = '''{"merchantCode":"%s","username":"%s","merchantTransSN":"%s","amount":%s,"timestamp":"%s"}'''%(self.context['merchantCode'],self.context["member"].username,self.context['orderid'],self.context['amount'],int(time.time()))
        return m_str;
   
    ''' 取款 '''
    def createWithdrawalStr(self,kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","merchantTransSN":"%s","amount":%s,"timestamp":"%s"}'''%(self.context['merchantCode'],self.context["member"].username,self.context['orderid'],self.context['amount'],int(time.time()))
        return m_str;

    ''' 取回钱包 '''

    def getbalanceStr(self, name,amount):
        m_str = '''{"merchantCode":"%s","username":"%s","merchantTransSN":"%s","amount":%s,"timestamp":"%s"}''' % (
        self.context['merchantCode'], name, self.context['orderid'], amount,
        int(time.time()))
        return m_str;

    '''投注记录'''
    def createBetRecordStr(self, kargs):
        if 'pageIndex' not in kargs:
            kargs['pageIndex'] = 1
        m_str = '''{"merchantCode":"%s","startDate":"%s","endDate":"%s","pageIndex":"%s","pageSize":"%s","timestamp":"%s"}'''%(self.context['merchantCode'],kargs['startDate'],kargs['endDate'],kargs['pageIndex'],10,str(int(time.time())))
        return m_str
    
    '''验证api接口返回的数据是否正确，并返回数据
    def validateAndReturn(self,m_data,errorCode,errorMsg):
        print(m_data)
        if m_data is None:
            return {"success": False,'errorCode': 3000,'errorMsg': "没获取到数据"}
        #将字符串转换成json
        m_json = json.loads(m_data)
        if m_json['Success']:
            if m_json.__contains__('Data'):
                return {"success": True,"data" : m_json['Data']}
        else:
            return {"success": False,'errorCode': errorCode,'errorMsg': errorMsg}
    '''
    '''通过娱乐城api接口获取游戏列表''' 
    def getGameListByAPI(self):
        m_str = '''{"merchantCode":"%s","timestamp":"%s"}'''%(self.context['merchantCode'],int(time.time()))
        m_url = self.context['apidomain'] + self.gameListURL
        m_headers = {'Content-Type':'text/plain'}
        m_data = self.sign(m_str)
        #发送规定格式的字符串base64(param)+"."+md5
        m_response = self.doPost(m_url, m_data, m_headers)
        print(m_response.text)
        return m_response.text
    
    '''在本地获取游戏列表'''
    def getGameListByLocal(self):
        return self.context['gameList']

    # 投注记录存数据库
    def saveBetRecordsToDB(self, eccode, gameType, newRecords):
        current_app.logger.info('PT同步交易数据:%s条'%(len(newRecords)))
        from app.entertainmentcity.EntertainmentCityEnum import PTEnum
        for record in newRecords:
            gamename = record['GameName']
            rechose= re.compile(r'[(](.*?)[)]', re.S)
            gametype = (re.findall(rechose, gamename))
            gametype = (' '.join(gametype))
            if record['Bet'] != 0:
                try:
                    dao = EntertainmentCityBetsDetail()
                    dao.ECCode = eccode
                    dao.childType = 1004
                    dao.BillNo = record['GameCode']
                    dao.PlayerName = record['PlayerName'].split(self.context['qz'])[1:]
                    dao.GameType = gametype
                    try:
                        dao.GameTypeInfo = gametype + '-' + PTEnum[gametype]
                    except Exception as e:
                        current_app.logger.exception('%s没有找到对应的KindID:%s'%(eccode,gametype))
                    dao.BetAmount = record['Bet']
                    dao.ValidBetAmount = record['Bet']
                    dao.CusAccount = record['Win']
                    dao.Profit = dao.CusAccount - dao.ValidBetAmount
                    dao.BetTime = time.mktime(time.strptime(record['GameDate'], "%Y-%m-%dT%H:%M:%S"))
                    dao.ReckonTime = dao.BetTime
                    dao.BeforeCredit = record['Balance'] - record['Win'] + record['Bet']
                    dao.Balance = record['Balance']
                    dao.Currency = "CNY"
                    try:
                        if record['CreateDateTime']:
                            dao.CreateDateTime = time.mktime(time.strptime(record['CreateDateTime'].split('.')[0], "%Y-%m-%dT%H:%M:%S"))
                        if record['UpdateDateTime']:
                            dao.UpdateDateTime = time.mktime(time.strptime(record['UpdateDateTime'].split('.')[0], "%Y-%m-%dT%H:%M:%S"))
                    except Exception as e:
                        current_app.logger.exception(e)
                    dao.extension = str(record)
                    dao.insertTime = int(time.time())
                    db.session.add(dao)
                except Exception as e:
                    current_app.logger.exception(e)
                    current_app.logger.error('%s交易记录同步错误:%s' % (eccode, record))
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            db.session.remove()
            raise Exception(format(e))
