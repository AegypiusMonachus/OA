import time,hashlib
from app.common.utils import defaultDateTime,dateToAmericaTime,AmericaTimeToDateTime
from app.entertainmentcity.abstractEntertainmentCity import AbstractEntertainmentCity
from app.models import db
from app.models.entertainment_city_bets_detail import EntertainmentCityBetsDetail
from flask import current_app
'''
    AG Entertainment City
'''

class AGEntertainmentCity(AbstractEntertainmentCity):
    gameListURL = '/API/AG/GetGameList'
    registerURL = '/API/AG/Register'
    loginURL = '/API/AG/Login'
    MobileLoginURL = '/API/AG/MobileLogin'
    balanceURL = '/API/AG/Balance'
    depositURL = '/API/AG/Deposit'
    withdrawalURL = '/API/AG/Withdrawal'
    checkTransferURL = '/API/AG/CheckTransfer'
    betRecordURL = '/API/AG/BetRecord'
    def createLoginStr(self,kargs):
        if kargs['deviceTypeCode'] == 'PC':
            m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","extension":{"oddsTypeCode":"%s","gameTypeCode":"%s","isDemo":"%s"},"timestamp":"%s"}'''%(self.context['merchantCode'],self.context["member"].username,
                         self.context['token'],'A',kargs['gameCode'],
                         kargs['isDemo'],int(time.time()))
        elif kargs['deviceTypeCode'] == 'Mobile':
            m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","extension":{"languageCode":"%s","currencyCode":"%s","oddsTypeCode":"%s","gameTypeCode":"%s","isDemo":"%s"},"timestamp":"%s"}'''%(self.context['merchantCode'],self.context["member"].username,
                         self.context['token'],'zhCN','CNY','A',kargs['gameCode'],
                         kargs['isDemo'],int(time.time()))
            loginURL = '/API/AG/MobileLogin'
        return m_str;

    def createRegisterStr(self):
        m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","extension":{"oddsTypeCode":"%s","languageCode":"%s","isDemo":"%s"},"timestamp":"%s"}'''%(self.context['merchantCode'],self.context["member"].username,
                     self.context['token'],'C','zhCN',
                     self.context['member'].isTsetPLay,int(time.time()))
        return m_str;
    
    def createBalanceStr(self,kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","extension":{"languageCode":"%s"},"timestamp":"%s"}'''%(self.context['merchantCode'],self.context["member"].username,
                     self.context['token'],'zhCN',int(time.time()))
        return m_str;

    ''' 更新钱包 '''
    def updateBalanceStr(self,kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","timestamp":"%s"}'''%(self.context['merchantCode'],kargs,self.context['token'],int(time.time()))
        return m_str;

    ''' 取回钱包 '''

    def getbalanceStr(self, name,amount):
        m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","merchantTransSN":"%s","amount":%s,"timestamp":"%s"}''' % (
        self.context['merchantCode'], name,self.context['token'], self.context['orderid'], amount,
        int(time.time()))
        return m_str;

    def createDepositStr(self):
        m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","merchantTransSN":%s,"amount":%s,"timestamp":"%s"}'''%(self.context['merchantCode'],self.context["member"].username,self.context['token'],self.context['orderid'],self.context['amount'],int(time.time()))
        return m_str;
    
    def createWithdrawalStr(self,kargs):
        m_str = '''{"merchantCode":"%s","username":"%s","token":"%s","merchantTransSN":%s,"amount":%s,"timestamp":"%s"}'''%(self.context['merchantCode'],self.context["member"].username,self.context['token'],self.context['orderid'],self.context['amount'],int(time.time()))
        return m_str;

    def createCheckTransferStr(self,kargs):
        m_str = '''{"merchantCode":"%s","merchantTransSN":%s,"timestamp":"%s"}'''%(self.context['merchantCode'],kargs['merchantTransSN'],int(time.time()))
        return m_str;
        
    def createBetRecordStr(self,kargs):
        if 'gameType' in kargs:
            gameType = kargs['gameType']
        else:
            current_app.logger.error('参数错误没有gameType')
            raise Exception("参数错误没有gameType")
        if gameType != 'Hunter':
            kargs['startDate'] = dateToAmericaTime(kargs['startDate'])
            kargs['endDate'] = dateToAmericaTime(kargs['endDate'])
        if 'pageIndex' not in kargs:
            kargs['pageIndex'] = 1
        m_str = '''{"merchantCode":"%s","gameType":"%s","startDate":"%s","endDate":"%s","pageIndex":"%s","pageSize":"%s","timestamp":"%s"}'''%(self.context['merchantCode'],kargs['gameType'],kargs['startDate'],kargs['endDate'],kargs['pageIndex'],20,str(int(time.time())))
        return m_str;
    '''获取游戏列表'''
    def gameList(self,type):
        m_data = self.context['gameList']
        return self.validateAndReturn(m_data,3003,"获取游戏列表失败")
    
    def saveBetRecordsToDB(self,eccode,gameType,newRecords):
        current_app.logger.info('AG-%s同步交易数据:%s条'%(gameType,len(newRecords)))
        from app.entertainmentcity.EntertainmentCityEnum import (AGEnum,ECTypeEnum)
        for record in newRecords:
            try:
                dao = EntertainmentCityBetsDetail()
                dao.ECCode = eccode
                dao.BillNo = record['BillNo']
                dao.childType = ECTypeEnum[gameType].value
                dao.childCode = gameType
                if gameType == 'Live':
                    dao.PlayerName = record['PlayerName'].split(self.context['qz'])[1:]
                    dao.BetAmount = record['BetAmount']
                    if record['ValidBetAmount']:
                        dao.ValidBetAmount = record['ValidBetAmount']
                    else :
                        dao.ValidBetAmount = record['BetAmount']
                    dao.Profit = float(record['NetAmount'])#收益
                    dao.CusAccount = dao.Profit +dao.ValidBetAmount
                    dao.BeforeCredit = float(record['BeforeCredit'])
                    dao.Balance = dao.BeforeCredit + dao.ValidBetAmount
                    dao.TableCode = record['TableCode']
                    dao.Remark = record['Remark']
                    dao.Result = record['Result']
                    dao.DeviceType = record['DeviceType']
                    try:
                        dao.BetTime = AmericaTimeToDateTime(record['BetTime'].split('.')[0])
                    except Exception as e:
                        current_app.logger.exception(e)
                        dao.BetTime = int(time.time())
                    try:  
                        dao.ReckonTime = AmericaTimeToDateTime(record['RecalcuTime'].split('.')[0])
                    except Exception as e:
                        current_app.logger.exception(e)
                        dao.ReckonTime = int(time.time())
                elif gameType == 'Hunter':
                    dao.PlayerName = record['UserName'].split(self.context['qz'])[1:]
                    dao.BetAmount = float(record['Cost'])
                    dao.ValidBetAmount = dao.BetAmount
                    dao.CusAccount = float(record['Earn'])
                    dao.Profit = dao.CusAccount - dao.BetAmount
                    dao.RoomID = record['RoomID']
                    dao.Remark = record['Remark']
                    try:
                        dao.BetTime = defaultDateTime(record['StartTime'].split('.')[0])
                    except Exception as e:
                        current_app.logger.exception(e)
                        dao.BetTime = int(time.time())
                    try:
                        dao.ReckonTime = defaultDateTime(record['EndTime'].split('.')[0])
                    except Exception as e:
                        current_app.logger.exception(e)
                        dao.ReckonTime = int(time.time())
                    dao.bet = record['RoomBet']
                else:
                    dao.PlayerName = record['UserName'].split(self.context['qz'])[1:]
                    dao.BetAmount = record['Account']
                    if record['ValidAccount']:
                        dao.ValidBetAmount = record['ValidAccount']
                    else :
                        dao.ValidBetAmount = dao.BetAmount
                    dao.Profit = float(record['CusAccount'])#收益
                    dao.CusAccount = dao.Profit +dao.ValidBetAmount
                    dao.BeforeCredit = record['SrcAmount']
                    if record['DstAmount']:
                        dao.Balance = record['DstAmount']
                    else:
                        dao.Balance = dao.BeforeCredit + dao.CusAccount
                    try:    
                        dao.BetTime = AmericaTimeToDateTime(record['BillTime'].split('.')[0])
                    except Exception as e:
                        current_app.logger.exception(e)
                        dao.BetTime = int(time.time())
                    try:
                        dao.ReckonTime = AmericaTimeToDateTime(record['ReckonTime'].split('.')[0])
                    except Exception as e:
                        current_app.logger.exception(e)
                        dao.ReckonTime = int(time.time())
                    if 'SimplifiedResult' in record and record['SimplifiedResult']:
                        dao.Result = record['SimplifiedResult']
                    if 'GMCode' in record and record['GMCode']:
                        dao.DeviceType = record['GMCode']
                    if 'DeviceType' in record:
                        dao.DeviceType = record['DeviceType']
                if 'GameType' in record:
                    dao.GameType = record['GameType']
                    if record['GameType'] in AGEnum: 
                        dao.GameTypeInfo = record['GameType'] + '-' + AGEnum[record['GameType']]
                    else:
                        current_app.logger.error('%s没有找到对应的KindID:%s'%(eccode,record['GameType']))
                if 'GameCode' in record:
                    dao.GameCode = record['GameCode']
                if 'PlayType' in record and record['PlayType']:  
                    dao.PlayType = record['PlayType']
                    dao.PlayTypeInfo = record['PlayType'] + '-' + AGEnum[record['PlayType']]
                if 'SlotType' in record and record['SlotType']:
                    dao.MachineType = record['SlotType']
#                 if "NetAmount" in newRecords:
#                     dao.NetAmount = newRecords['NetAmount']
                if 'ProductID' in record and record['ProductID']:
                    dao.ProductID = record['ProductID']
                if 'ExttxID' in record and record['ExttxID']:
                    dao.ExttxID = record['ExttxID']
                #dao.ReckonTime = newRecords['']
                if 'Flag' in record and record['Flag']:
                    dao.Flag = record['Flag']
                if 'Currency' in record and record['Currency']:
                    dao.Currency = record['Currency']
                if 'BetIP' in record and record['BetIP']:
                    dao.BetIP = record['BetIP']
                if 'PlatformType' in record and record['PlatformType']:
                    dao.PlatformType = record['PlatformType']
                try:
                    if 'CreateDateTime' in record and record['CreateDateTime']:
                        dao.CreateDateTime = time.mktime(time.strptime(record['CreateDateTime'].split('.')[0], "%Y-%m-%dT%H:%M:%S"))
                    if 'UpdateDateTime' in record and record['UpdateDateTime']:
                        dao.UpdateDateTime = time.mktime(time.strptime(record['UpdateDateTime'].split('.')[0], "%Y-%m-%dT%H:%M:%S"))
                except Exception as e:
                    current_app.logger.exception(e)
                dao.insertTime = int(time.time())
                dao.extension = str(record)
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