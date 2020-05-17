import json,time
from app.entertainmentcity.abstractEntertainmentCity import AbstractEntertainmentCity
from app.models import db
from app.models.entertainment_city_bets_detail import EntertainmentCityBetsDetail
from flask import current_app
'''
    KAIYUAN Entertainment City
'''
class KAIYUANEntertainmentCity(AbstractEntertainmentCity):
    loginURL = '/API/KAIYUAN/Login'
    balanceURL = '/API/KAIYUAN/Balance'
    depositURL = '/API/KAIYUAN/Deposit'
    withdrawalURL = '/API/KAIYUAN/Withdrawal'
    checkTransferURL = '/API/KAIYUAN/CheckTransfer'
    betRecordURL = '/API/KAIYUAN/BetRecord'
    # 登录
    def createLoginStr(self, kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","extension":{"gameCode":"%s"},"timestamp":"%s"}''' % (
        self.context['merchantCode'], self.context["member"].username,
        self.context['token'], kargs['gameCode'], int(time.time()))
        return m_str;

    # def createRegisterStr(self):
    #     m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","extension":{"oddsTypeCode":"%s","languageCode":"%s","isDemo":"%s"},"timestamp":"%s"}''' % (
    #     self.context['merchantCode'], self.context["member"].username,
    #     self.context['token'], 'C', 'zhCN',
    #     self.context['member'].isTsetPLay, int(time.time()))
    #     return m_str;

    # 余额
    def createBalanceStr(self, kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","timestamp":"%s"}''' % (
        self.context['merchantCode'], self.context["member"].username, int(time.time()))
        return m_str;

    ''' 更新钱包 '''
    def updateBalanceStr(self,kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","timestamp":"%s"}'''%(self.context['merchantCode'],kargs,int(time.time()))
        return m_str;

    ''' 取回钱包 '''

    def getbalanceStr(self, name,amount):
        m_str = '''{"merchantCode":"%s","username":"%s","merchantTransSN":"%s","amount":%s,"timestamp":"%s"}''' % (
        self.context['merchantCode'], name, self.context['orderid'], amount,
        int(time.time()))
        return m_str;

    # 存款
    def createDepositStr(self):
        m_str = '''{"merchantCode":"%s","username":"%s","merchantTransSN":%s,"amount":%s,"timestamp":"%s"}''' % (
        self.context['merchantCode'], self.context["member"].username, self.context['orderid'],
        self.context['amount'], int(time.time()))
        return m_str;
    # 提款
    def createWithdrawalStr(self, kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","merchantTransSN":%s,"amount":%s,"timestamp":"%s"}''' % (
        self.context['merchantCode'], self.context["member"].username, self.context['orderid'],
        self.context['amount'], int(time.time()))
        return m_str;
    # 检查转帐
    def createCheckTransferStr(self, kargs):
        m_str = '''{"merchantCode":"%s","GameTransSN":"%s","timestamp":"%s"}''' % (
        self.context['merchantCode'], kargs['GameTransSN'],int(time.time()))
        return m_str;
    # 投注纪录
    def createBetRecordStr(self, kargs):
        if 'pageIndex' not in kargs:
            kargs['pageIndex'] = 1
        m_str = '''{"merchantCode":"%s","startDate":"%s","endDate":"%s","pageIndex":"%s","pageSize":"%s","timestamp":"%s"}'''%(self.context['merchantCode'],kargs['startDate'],kargs['endDate'],kargs['pageIndex'],10,str(int(time.time())))
        return m_str;

    '''获取游戏列表'''
    
    def register(self):
        return {"success": True}
    
    def gameList(self, type):
        m_data = self.context['gameList']
        return self.validateAndReturn(m_data, 3003, "获取游戏列表失败")

    def saveBetRecordsToDB(self,eccode,gameType,newRecords):
        current_app.logger.info('KAIYUAN同步交易数据:%s条'%(len(newRecords)))
        from app.entertainmentcity.EntertainmentCityEnum import KAIYUANEnum
        for record in newRecords:
            try:
                dao = EntertainmentCityBetsDetail()
                dao.ECCode = eccode
                dao.childType = 1003
                dao.BillNo = record['GameID']
                dao.PlayerName = record['Account'].split(self.context['qz'])[1:]
                dao.GameType = record['KindID']
                if record['KindID'] in KAIYUANEnum:
                    dao.GameTypeInfo = record['KindID'] + '-' + KAIYUANEnum[record['KindID']]
                else:
                    current_app.logger.error('%s没有找到对应的KindID:%s'%(eccode,record['KindID']))
                dao.BetAmount = float(record['AllBet'])
                dao.ValidBetAmount = float(record['AllBet'])
                dao.Profit = float(record['Profit'])
                dao.CusAccount = dao.ValidBetAmount + dao.Profit
                if record['GameStartTime']:
                    dao.BetTime = time.mktime(time.strptime(record['GameStartTime'], "%Y-%m-%dT%H:%M:%S"))
                if record['GameEndTime']:
                    dao.ReckonTime = time.mktime(time.strptime(record['GameEndTime'], "%Y-%m-%dT%H:%M:%S"))
                dao.RoomID = record['ServerID']
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
                current_app.logger.error('%s交易记录同步错误:%s'%(eccode,record))
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            db.session.remove()
            raise Exception(format(e))
                
                
                
                
