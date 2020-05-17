import time
from app.models import db
from app.models.entertainment_city_log import EntertainmentCityLog,EntertainmentCityTradeLog,EntertainmentCityTradeDetail
from app.entertainmentcity import EntertainmentCityFactory
from app.models.member import Member
from app.models.member_account_change import MemberAccountChangeRecord
from app.common.orderUtils import createECOrderId
from flask import current_app
from flask_restful import abort
'''
额度转换
'''

class AmountTransfer():
    '''
        从指定的娱乐城转账到主账户
    '''
    @staticmethod
    def withdrawalToAccount(context,kargs):
        uid = context['member'].id
        username = context['member'].username
        isTsetPLay = context['member'].isTsetPLay
        actionTime = int(time.time())
        last_ce = None;
        ecTradeDao = None;
        if 'isDemo' in kargs:
            if kargs['isDemo'] == '1' or isTsetPLay == 1:
                current_app.logger.info('%s试玩账号不需要额度转换'%(username))
                return {"success": True}
        if 'fromEC' in kargs and kargs['fromEC'] is not None:
            last_ce = kargs['fromEC']
        else:
            #获取上一次用户登录的娱乐城
            ecLogDao = EntertainmentCityLog()
            last_ce = ecLogDao.getLastLogin(uid)
        if last_ce is None:
            return {"success": True}
        current_app.logger.info("%s本次娱乐城：%s"%(username,context['loginEC']))
        current_app.logger.info("%s上次娱乐城：%s"%(username,last_ce))
        #如果本次与上一次登录的是同一个娱乐城或者上一次在kk。则不用转账
        if (last_ce == "MAIN") or (last_ce == context['loginEC']):
            current_app.logger.info('%s不需要取款'%(username))
            return {"success": True}
        amount = None;
        lastEC = EntertainmentCityFactory.getEntertainmentCity(last_ce)
        lastEC.context["member"] = context["member"]
        #去上一个娱乐城查询余额
        try:
            m_res = lastEC.balance(kargs)
            if m_res['success'] == False:
                current_app.logger.error("%s查询余额错误:%s"%(username,m_res))
                return {"success": False,'errorCode': 3001,'errorMsg': "查询余额错误"} 
        except Exception as e:
            current_app.logger.exception(format(e))
            current_app.logger.error("%s查询余额错误:%s"%(username,m_res))
            return {"success": False,'errorCode': 3001,'errorMsg': "查询余额错误"}  
        #娱乐城的余额
        balance = float(m_res['data']['balance'])
        current_app.logger.info('%s在%s余额：%s'%(username,last_ce,balance))
        if 'amount' in kargs:
            amount = kargs['amount'];
            current_app.logger.info('%s从%s取款：%s'%(username,last_ce,amount))
            if amount > balance:
                current_app.logger.info("%s取款金额大于娱乐城余额，余额是%s"%(username,balance))
                return {"success": False,'errorCode': 3001,'errorMsg': "转账失败"}
            else:
                balance = amount
        lastEC.context["amount"] = balance
        orderid = createECOrderId(uid);
        lastEC.context['orderid'] = orderid
        wjorderId = None;
        #取款
        if balance >=1:
            current_app.logger.info('开始取款')
            #生成交易记录
            ecTradeDao = AmountTransfer.saveECTradeLog(uid, username, balance, actionTime, 'MAIN',last_ce, orderid, None, context['real_ip'],0,0)
            try:
                m_res = lastEC.withdrawal(None)
            except Exception as e:
                current_app.logger.exception(e)
                current_app.logger.error('%s从%s取款失败'%(username,last_ce))
                AmountTransfer.updateECTradeLog(ecTradeDao,None,0,0,0)
                #生成交易明细
                AmountTransfer.saveECTradeDetail(uid, username, actionTime, balance, orderid, last_ce, None, 0, '娱乐城取款失败，不用额度确认',None)
#                 AmountTransfer.saveECTradeLog(uid, username, balance, actionTime, 'MAIN',last_ce, orderid, wjorderId, context['real_ip'],2,0,'娱乐城转账失败,余额已从娱乐城转出,需要人工审核结案')
                return {"success": False,'errorCode': 3001,'errorMsg': "转账失败"} 
            if m_res['success'] == False:
                current_app.logger.error('%s从%s取款失败:%s'%(username,last_ce,m_res))
                AmountTransfer.updateECTradeLog(ecTradeDao,None,0,0,0)
                AmountTransfer.saveECTradeDetail(uid, username, actionTime, balance, orderid, last_ce, None, 0, '娱乐城取款失败，不用额度确认',None)
                return {"success": False,'errorCode': 3001,'errorMsg': "转账失败"}
            wjorderId = AmountTransfer.getWjorderId(m_res,last_ce);
            AmountTransfer.updateECTradeLog(ecTradeDao,wjorderId,0,1,2)
            AmountTransfer.saveECTradeDetail(uid, username, actionTime, balance, orderid, last_ce, None, 1, '交易成功',None)
            current_app.logger.info('%s结束取款'%(username))
            current_app.logger.info('%s取出余额：%s'%(username,balance))
        else:
            current_app.logger.info('%s结束取款取款金额小于1元'%(username))
            return {"success": True}
        #将余额存回主账户
        current_app.logger.info("%s转回主账户开始"%(username))
        #如果钱已经从娱乐城取出，但是更新主账户金额时发生错误(例如数据库链接不上),需要日志记录，否前钱不回来
        try:
            member = Member.amountToMemberAccount(username, balance)
        except Exception as e:
            current_app.logger.exception(e)
            current_app.logger.error("%s转回主账户失败，内部错误%s"%(username,e))
            current_app.logger.error("%s从%s娱乐城取款%s已经完成，但是将金额更新回主账户时错误,请查看详细日志。"%(username,last_ce,balance))
            current_app.logger.error({"success": False,'errorCode': 9001,'errorMsg': "%s从%s娱乐城取款%s已经完成，但是将金额更新回主账户时错误,这是一个严重错误,需要人工存入"%(username,last_ce,balance)})
            AmountTransfer.updateECTradeLog(ecTradeDao,wjorderId,0,1,2,0,"%s从%s娱乐城取款%s已经完成，将余额存入回主账户的过程中发生错误,这是一个严重错误,需要人工存入"%(username,last_ce,balance),'确认转账状态与判断不符而造成掉额度，开始进行补额度 - [系統]')
            AmountTransfer.saveECTradeDetail(uid, username, actionTime, balance, orderid, 'MAIN', 1, 2, '交易失败','确认转账状态与判断不符而造成掉额度，开始进行补额度 - [系統]')
            return {"success": False,'errorCode': 3001,'errorMsg': "转账失败"} 
        current_app.logger.info("转回主账户完成")
        AmountTransfer.updateECTradeLog(ecTradeDao,wjorderId,1,1,1,None,'转账成功',None)
        AmountTransfer.saveCoinlog(uid, balance, member, actionTime, orderid, wjorderId, 'MAIN', last_ce, context['ip'],400,'转回主账户完成')
        AmountTransfer.saveECTradeDetail(uid, username, actionTime, balance, orderid, 'MAIN', None, 1, '交易成功',None)
        return {"success": True}
    
    '''
        将主账户的钱转到指定娱乐城
    ce：选择登录的娱乐城
    '''
    @staticmethod        
    def accountToEntertainmentCity(context,kargs,ec):
        current_app.logger.info('从主账户转账到%s 开始'%(context['loginEC']))
        uid = context['member'].id
        username = context['member'].username
        isTsetPLay = context['member'].isTsetPLay
        if kargs['isDemo'] == '1' or isTsetPLay == 1:
            current_app.logger.info('试玩不需要取款')
            return {"success": True}  
        wjorderId = None #娱乐城订单号
        amount = None    #转账金额，单独调用转账接口时使用
        ecTradeDao = None;
        if 'amount' in kargs:
            amount = kargs['amount'];
        member = Member.query.filter(Member.username == username).first()
        balance = member.balance
        if amount is not None:
            if amount > balance :
                current_app.logger.info('%s转款金额大于余额'%(username))
                return {"success": False,'errorCode': 3001,'errorMsg': "转账失败,余额不足"}  
        else:
            amount = balance
        if amount < 1:
            current_app.logger.info('%s余额小于1元不进行转账'%(username))
            return {"success": True} 
        orderid = createECOrderId(uid)
        actionTime = int(time.time())
        ecTradeDao = AmountTransfer.saveECTradeLog(uid, username, amount, actionTime, context['loginEC'],'MAIN', orderid, None, context['real_ip'],0,1)
        #1：先冻结余额
        member.balance -= amount
        #member.frozenBalance += amount
        db.session.add(member)
        try:
            db.session.commit()
            AmountTransfer.saveECTradeDetail(uid, username, actionTime, amount, orderid, 'MAIN', None, 1, '交易成功',None)
        except Exception as e:
            db.session.rollback()
            db.session.remove()
            current_app.logger.error('%s从主账户取款错误,用户金额已回滚：%s'%(username,e))
            #AmountTransfer.saveECTradeLog(uid, username, amount, actionTime, context['loginEC'], 'MAIN',orderid, wjorderId, context['real_ip'],0,1,'从主账户取款错误,用户金额已回滚')  
            return {"success": False,'errorCode': 3001,'errorMsg': "转账失败"}  
        AmountTransfer.saveCoinlog(uid, -amount, member, int(time.time()), orderid, None, context['loginEC'], 'MAIN', context['ip'],110,'娱乐城转账')
        AmountTransfer.updateECTradeLog(ecTradeDao,None,1,0,0)
        #2：将资金转入娱乐城
        try:
            ec.context['orderid'] = orderid
            ec.context["amount"] = amount
            m_res = ec.deposit()
            #如果存款时发生异常
            if m_res['success'] == False:
                current_app.logger.error('%s转账到娱乐城发生错误：%s'%(username,m_res))
                #return {"success": False,'errorCode': 3000,'errorMsg': "转账到娱乐城发生错误"}
                raise Exception("%s转账到娱乐城发生错误"%(m_res))
        except Exception as e:
            current_app.logger.exception(e)
            current_app.logger.error('%s转账到娱乐城发生错误：%s'%(username,e))
            #如果发生异常将金额返还用户
            member.balance += amount
#             member.frozenBalance -= amount
            db.session.add(member)
            try:
                db.session.add(member)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                db.session.remove()
                AmountTransfer.updateECTradeLog(ecTradeDao,None,1,0,2,0,"资金返还用户主账户失败,这是一个严重错误,需要手动返回&s用户%s资金"%(username,amount),'确认转账状态与判断不符而造成掉额度，需要进行补额度 - [系統]')
                current_app.logger.error('%s冻结资金返还用户失败：%s'%(username,e))
                current_app.logger.error({"success": False,'errorCode': 9001,'errorMsg': "资金返还用户主账户失败,这是一个严重错误,需要手动返回&s用户%s资金"%(username,amount)})
                return {"success": False,'errorCode': 3001,'errorMsg': "转账失败"}  
            AmountTransfer.saveCoinlog(uid, amount, member, int(time.time()), orderid, None, context['loginEC'], 'MAIN', context['ip'],111,'娱乐城转账失败资金返还')
            AmountTransfer.updateECTradeLog(ecTradeDao,None,99,0,0,1,'娱乐城转账失败资金返还',None)
            return {"success": False,'errorCode': 3001,'errorMsg': "转账失败"} 
        #如果转入娱乐城成功
        wjorderId = AmountTransfer.getWjorderId(m_res,context['loginEC']);
        AmountTransfer.updateECTradeLog(ecTradeDao,wjorderId,1,1,1,1,'转账成功')
        AmountTransfer.saveECTradeDetail(uid, username, actionTime, amount, orderid, context['loginEC'], None, 1, '交易成功',None)
        return {"success": True}
        
    @staticmethod 
    def saveECTradeLog(uid,username,amount,actionTime,ec,last_ce,orderid,wjorderId,ip,state,type,remark=None):
        mData = {}
        mData['uid'] = uid
        mData['username'] = username
        mData['actionTime'] = actionTime
        mData['ec'] = ec
        mData['last_ec'] = last_ce
        mData['amount'] = amount
        mData['orderid'] = orderid
        mData['wjorderId'] = wjorderId
        mData['real_ip'] = ip
        mData['state'] = state
        mData['type'] = type
        mData['remark'] = remark
        mData['is_automatic'] = 1
        dao = EntertainmentCityTradeLog(**mData)
        try:
            db.session.add(dao)
            db.session.commit()
            return dao
        except Exception as e:
            current_app.logger.error({"success": False,'errorCode': 9001,'errorMsg': "娱乐城交易记录(tb_entertainment_city_trade_log)写入错误:%s"%(mData)})
            current_app.logger.exception(e)
            raise Exception(e)
    @staticmethod 
    def updateECTradeLog(ecTradeDao,wjorderId,main_confirm,ec_confirm,state,is_automatic=None,remark=None,info=None):
        if ecTradeDao is None:
            return 
        if wjorderId is not None:
            ecTradeDao.wjorderId = wjorderId
        if main_confirm is not None:
            ecTradeDao.main_confirm = main_confirm
        if ec_confirm is not None:
            ecTradeDao.ec_confirm = ec_confirm
        if state is not None:
            ecTradeDao.state = state
        if remark is not None:
            ecTradeDao.remark = remark
        if info is not None:
            ecTradeDao.info = info
        if is_automatic is not None:
            ecTradeDao.is_automatic = is_automatic
        try:
            db.session.add(ecTradeDao)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            db.session.remove()
            current_app.logger.error({"success": False,'errorCode': 9001,'errorMsg': "娱乐城交易记录(tb_entertainment_city_trade_log)更新错误"})
    
    @staticmethod 
    def saveECTradeDetail(uid,username,actionTime,amount,orderid,eccode,type,state,remark,info):
        mData = {}
        mData['uid'] = uid
        mData['username'] = username
        mData['actionTime'] = actionTime
        mData['ec'] = eccode
        mData['amount'] = amount
        mData['orderid'] = orderid
        mData['state'] = state
        mData['remark'] = remark
        mData['type'] = type
        mData['info'] = info
        dao = EntertainmentCityTradeDetail(**mData)
        try:
            db.session.add(dao)
            db.session.commit()
        except Exception as e:
            current_app.logger.error({"success": False,'errorCode': 9001,'errorMsg': "娱乐城交易明细(tb_entertainment_city_trade_detail)写入错误"})
            current_app.logger.exception(e)
     
    @staticmethod 
    def saveECLog(uid,username,actionTime,ec,ip):
        mData = {}
        mData['uid'] = uid
        mData['username'] = username
        mData['actionTime'] = actionTime
        mData['ec'] = ec
        mData['ip'] = ip
        dao = EntertainmentCityLog()
        try:
            dao.insert(**mData)
        except Exception as e:
            current_app.logger.error("需要手动更新娱乐城登录日志表，否则会导致下次额度转换错误")
            current_app.logger.error({"success": False,'errorCode': 9001,'errorMsg': "娱乐城登录日志写入错误:%s"%(mData)})
            current_app.logger.exception(e)
                   
    @staticmethod 
    def saveCoinlog(uid,amount,member,actionTime,orderid,wjorderId,ce,last_ce,ip,type,info): 
        conLogDao = MemberAccountChangeRecord()
        mData = {}
        mData['memberId'] = uid
#         if last_ce == 'MAIN':
#             mData['amount'] = -amount
#         else:
#             mData['amount'] = amount
        mData['amount'] = amount
        mData['memberBalance'] = member.balance
        mData['memberFrozenBalance'] = member.frozenBalance
        mData['accountChangeType'] = type
        mData['time'] = actionTime
        mData['orderId'] = orderid
        mData['extfield1'] = ce
        mData['extfield2'] = last_ce
        mData['rechargeid'] = wjorderId
        mData['host'] = ip
        mData['info'] = info
        try:
            conLogDao.insert(**mData)
        except Exception as e:
            current_app.logger.exception(e)
            
    @staticmethod 
    def getWjorderId(res,eccode):
        if eccode == 'AG':
            return res['data']['MerchantTransSN'];
        if eccode == 'PT':
            return res['data']['MerchantTransSN'];
        if eccode == 'KAIYUAN':
            return res['data']['GameTransSN'];
