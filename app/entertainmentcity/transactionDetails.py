from app.redis.redisConnectionManager import CERedisManager
from app.models.entertainment_city_bets_detail import EntertainmentCityBetsDetail
from app.models.entertainment_city import EntertainmentCity
from app.entertainmentcity import EntertainmentCityFactory
# from app.entertainmentcity import scheduler
from app.schedule import scheduler
import datetime,time,json
from flask import current_app
from app.models import db
from app.entertainmentcity.EntertainmentCityEnum import billNoEnum

'''从数据库取出交易记录放到redis中'''
def ecBetsDetailsToRedis(startDateTime,endDateTime):
    with CERedisManager.app.app_context():
        dao = EntertainmentCityBetsDetail()
        results = dao.getGroupData(startDateTime, endDateTime)
        redisImpl = CERedisManager.get_redisImpl()
        redisImpl.flushdb()
        for result in results:
            billNo = result[0]
            eccode = result[1]
            if result[2] is not None and result[2] !='':
                eccode = eccode +'-' + str(result[2])
            #current_app.logger.info('%s:%s'%(eccode, billNo))
            redisImpl.set(eccode, billNo)

'''从redis中获取上一次交易信息 '''          
def getBetsDetailsFromRedis(eccode):
    with CERedisManager.app.app_context():
        redisImpl = CERedisManager.get_redisImpl()
        return redisImpl.get(eccode)
    
'''将订单集合存入redis中 '''          
def setBetsDetailsToRedis(eccode,value):
    with CERedisManager.app.app_context():
        redisImpl = CERedisManager.get_redisImpl()
        redisImpl.set(eccode, value)

"""获取数据库最新的娱乐城名称"""
def getECByDB():
    m_results = []
    m_query = db.session.query(EntertainmentCity.code).all()
    for names in m_query:
        m_results.append(names[0])
    return m_results
   
"""获取所有交易记录"""
def getAllBetRecords(ceEntity, gameType ,startDate, endDate):
    ceCode = ceEntity.context['code']
    kargs = {'startDate':startDate,'endDate':endDate}
    if gameType is not None:
        kargs['gameType'] = gameType
    #向娱乐城请求交易记录
    m_response = ceEntity.betRecord(kargs)
    #验证返回结果
    status_code = m_response.status_code
    if status_code >= 400:
        current_app.logger.error('请求%s交易记录失败：%s'%(ceCode,m_response))
        raise Exception("请求%s交易记录失败", m_response)
    #解析分页信息
    allRecords = []
    respJson = json.loads(m_response.text)
    #先解析第一次请求的数据
    records = analysisPagination(respJson)
    if records:
        allRecords.extend(records)
    if 'Pagination' in respJson:
        pagination = respJson['Pagination']
        if 'TotalCount' not in pagination or pagination['TotalCount'] == 0:
            return None
        if 'PageCount' in pagination and pagination['PageCount'] > 0:
            pageCount = pagination['PageCount']
            if pageCount == 1:
                return allRecords
            for pageIndex in range(2,pageCount+1):
                kargs['pageIndex'] = pageIndex
                kargs['startDate'] = startDate
                kargs['endDate'] = endDate
                m_response = ceEntity.betRecord(kargs)
                status_code = m_response.status_code
                if status_code >= 400:
                    current_app.logger.error('请求%s交易记录失败：pageIndex = %s'%(ceCode,pageIndex))
                respJson = json.loads(m_response.text)
                records = analysisPagination(respJson)
                if records is not None:
                    allRecords.extend(records)
    return allRecords
    
'''分析页面信息获取数据'''
def analysisPagination(respJson):
    if 'Data' not in respJson:
        current_app.logger.error('交易记录格式错误：没有数据信息：%s'%(respJson))
        return None
    #先将当前页的数据加入到数组中
    try:
        if 'record' in respJson['Data']:
            return respJson['Data']['record']
    except Exception as e:
        current_app.logger.exception(e)
        current_app.logger.error('交易记录格式错误：没有数据信息：%s'%(respJson))
        return None

def diffBetRecords(eccode,gameType,newRecords,billNoField):
    #从redis中获取上一次交易信息
    #需要保存到redis中数据
    #records_redis = []
    #需要保存到DB中数据
    records_DB = []
    if gameType is not None and gameType !='':
        eccode = eccode + '-' + str(gameType)
    oldRecordsStr = getBetsDetailsFromRedis(eccode)
    oldList = None
    if oldRecordsStr is not None:
        oldList = json.loads(oldRecordsStr)
    current_app.logger.info('%s老数据 :%s'%(eccode,oldList))
    if oldList is None:
        for result in newRecords:
            try:
                billNo = result[billNoField]
                #records_redis.append(billNo)
                records_DB.append(result)
            except Exception as e:
                current_app.logger.exception(e)
                current_app.logger.error('%s交易记录解析错误'%(eccode,result))
    else:
        for result in newRecords:
            try:            
                billNo = result[billNoField]
                #records_redis.append(billNo)
                if billNo in oldList:
                    continue
                else:
                    records_DB.append(result)
            except Exception as e:
                current_app.logger.exception(e)
                current_app.logger.error('%s交易记录解析错误'%(eccode,result))
    #current_app.logger.info('diff后redis:%s'%(records_redis))
    current_app.logger.info('diff后mysql:%s'%(records_DB))            
    #setBetsDetailsToRedis(eccode,json.dumps(records_redis))
    return records_DB
    

def job_1(limit):
    timeStamp = int(time.time())
    startDate = (datetime.datetime.fromtimestamp(timeStamp) + datetime.timedelta(seconds=-limit+1)).strftime("%Y-%m-%d %H:%M:%S")
    endDate = (datetime.datetime.fromtimestamp(timeStamp)).strftime("%Y-%m-%d %H:%M:%S")
    with scheduler.app.app_context():
        current_app.logger.info('同步交易记录 %s至 %s 开始'%(startDate,endDate))
        ecList = getECByDB()
        try:
            for ec in ecList:
                if ec == 'kk':
                    continue
                current_app.logger.info('同步%s交易记录 %s至 %s 开始'%(ec,startDate,endDate))
                ceEntity = None
                try:
                    ceEntity = EntertainmentCityFactory.getEntertainmentCity(ec)
                except Exception as e:
                    current_app.logger.exception(e)
                    current_app.logger.error('同步%s数据异常 %s至 %s'%(ec,startDate,endDate))
                    continue
                if ec == 'AG':
                    gtList = ['Live','Slot','Hunter','Yoplay','Sport']
                    for gameType in gtList:
                        try:
                            records_DB = None
                            allRecords = getAllBetRecords(ceEntity,gameType,startDate,endDate)
                            #current_app.logger.info(allRecords)
                            if allRecords and allRecords is not None:
                                from app.entertainmentcity.EntertainmentCityEnum import ECTypeEnum
                                gameTypeCode = ECTypeEnum[gameType].value
                                records_DB = diffBetRecords(ec,gameTypeCode,allRecords,billNoEnum[ec].value)
                            if records_DB and records_DB is not None:
                                ceEntity.saveBetRecordsToDB(ec,gameType,records_DB)
                        except Exception as e:
                            current_app.logger.exception(e)
                            current_app.logger.error('同步%s-%s数据异常 %s至 %s'%(ec,gameType,startDate,endDate))
                if ec == 'PT':
                    allRecords = getAllBetRecords(ceEntity,ceEntity.context['gameTypes'],startDate,endDate)
                    #current_app.logger.info(allRecords)
                    try:
                        records_DB = None
                        if allRecords is not None:
                            records_DB = diffBetRecords(ec,ceEntity.context['gameTypes'],allRecords,billNoEnum[ec].value)
                        #allRecords = json.loads('[{"GameID":"50-1559618295-147909177-3","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020049","ChairID":"3","UserCount":"4","CellScore":"5.00","AllBet":"5.00","Profit":"-5.00","Revenue":"0.00","CardValue":"3d1d2236262b1119350b08170000001","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:18:15","GameEndTime":"2019-06-04T11:18:57","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:27:01.96"},{"GameID":"50-1559618346-147910646-4","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020116","ChairID":"4","UserCount":"5","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"2c04031b2a370c15223a09360a29333","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:19:06","GameEndTime":"2019-06-04T11:19:19","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:27:01.96"},{"GameID":"50-1559618361-147911112-4","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020270","ChairID":"4","UserCount":"3","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"0000001c0c332a28252908320000003","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:19:21","GameEndTime":"2019-06-04T11:19:36","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:27:01.96"},{"GameID":"50-1559618400-147912269-3","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020278","ChairID":"3","UserCount":"4","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"0c0522213b170b1a351129140000004","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:20:00","GameEndTime":"2019-06-04T11:20:11","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618385-147911824-4","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020004","ChairID":"4","UserCount":"5","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"1d2b132a09033a39352d04022505155","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:19:45","GameEndTime":"2019-06-04T11:20:21","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618421-147912848-4","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020261","ChairID":"4","UserCount":"3","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"0000002118162b17050b15230000002","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:20:21","GameEndTime":"2019-06-04T11:20:37","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618439-147913400-4","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020225","ChairID":"4","UserCount":"4","CellScore":"3.00","AllBet":"3.00","Profit":"10.45","Revenue":"0.55","CardValue":"2313190000003905142c0c033c0b374","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:20:39","GameEndTime":"2019-06-04T11:20:56","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618463-147914137-3","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020124","ChairID":"3","UserCount":"3","CellScore":"3.00","AllBet":"3.00","Profit":"2.85","Revenue":"0.15","CardValue":"0000002a09043313160d39320000003","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:21:03","GameEndTime":"2019-06-04T11:21:14","CreateDateTime":"2019-06-04T11:24:02.203","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618482-147914656-3","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020145","ChairID":"3","UserCount":"5","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"3118121d2c273d0b2a2d28220807144","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:21:22","GameEndTime":"2019-06-04T11:21:35","CreateDateTime":"2019-06-04T11:24:02.203","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618496-147915101-1","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020218","ChairID":"1","UserCount":"5","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"3c16250d2908012d3919370526061a5","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:21:36","GameEndTime":"2019-06-04T11:21:55","CreateDateTime":"2019-06-04T11:24:02.203","UpdateDateTime":"2019-06-04T11:30:02.48"}]')
                        if records_DB and records_DB is not None:
                            ceEntity.saveBetRecordsToDB(ec,ceEntity.context['gameTypes'],records_DB)
                    except Exception as e:
                        current_app.logger.exception(e)
                        current_app.logger.error('同步%s数据异常 %s至 %s'%(ec,startDate,endDate))
                if ec == 'KAIYUAN':
                    allRecords = getAllBetRecords(ceEntity, ceEntity.context['gameTypes'], startDate, endDate)
                    #current_app.logger.info(allRecords)
                    try:
                        records_DB = None
                        if allRecords is not None:
                            records_DB = diffBetRecords(ec, ceEntity.context['gameTypes'], allRecords, billNoEnum[ec].value)
                        # allRecords = json.loads('[{"GameID":"50-1559618295-147909177-3","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020049","ChairID":"3","UserCount":"4","CellScore":"5.00","AllBet":"5.00","Profit":"-5.00","Revenue":"0.00","CardValue":"3d1d2236262b1119350b08170000001","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:18:15","GameEndTime":"2019-06-04T11:18:57","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:27:01.96"},{"GameID":"50-1559618346-147910646-4","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020116","ChairID":"4","UserCount":"5","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"2c04031b2a370c15223a09360a29333","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:19:06","GameEndTime":"2019-06-04T11:19:19","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:27:01.96"},{"GameID":"50-1559618361-147911112-4","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020270","ChairID":"4","UserCount":"3","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"0000001c0c332a28252908320000003","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:19:21","GameEndTime":"2019-06-04T11:19:36","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:27:01.96"},{"GameID":"50-1559618400-147912269-3","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020278","ChairID":"3","UserCount":"4","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"0c0522213b170b1a351129140000004","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:20:00","GameEndTime":"2019-06-04T11:20:11","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618385-147911824-4","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020004","ChairID":"4","UserCount":"5","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"1d2b132a09033a39352d04022505155","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:19:45","GameEndTime":"2019-06-04T11:20:21","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618421-147912848-4","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020261","ChairID":"4","UserCount":"3","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"0000002118162b17050b15230000002","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:20:21","GameEndTime":"2019-06-04T11:20:37","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618439-147913400-4","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020225","ChairID":"4","UserCount":"4","CellScore":"3.00","AllBet":"3.00","Profit":"10.45","Revenue":"0.55","CardValue":"2313190000003905142c0c033c0b374","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:20:39","GameEndTime":"2019-06-04T11:20:56","CreateDateTime":"2019-06-04T11:21:02.437","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618463-147914137-3","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020124","ChairID":"3","UserCount":"3","CellScore":"3.00","AllBet":"3.00","Profit":"2.85","Revenue":"0.15","CardValue":"0000002a09043313160d39320000003","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:21:03","GameEndTime":"2019-06-04T11:21:14","CreateDateTime":"2019-06-04T11:24:02.203","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618482-147914656-3","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020145","ChairID":"3","UserCount":"5","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"3118121d2c273d0b2a2d28220807144","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:21:22","GameEndTime":"2019-06-04T11:21:35","CreateDateTime":"2019-06-04T11:24:02.203","UpdateDateTime":"2019-06-04T11:30:02.48"},{"GameID":"50-1559618496-147915101-1","Account":"600655_2nmqq123","ServerID":"2201","KindID":"220","TableID":"44020218","ChairID":"1","UserCount":"5","CellScore":"1.00","AllBet":"1.00","Profit":"-1.00","Revenue":"0.00","CardValue":"3c16250d2908012d3919370526061a5","ChannelID":"600655","LineCode":"600655_AUQI","GameStartTime":"2019-06-04T11:21:36","GameEndTime":"2019-06-04T11:21:55","CreateDateTime":"2019-06-04T11:24:02.203","UpdateDateTime":"2019-06-04T11:30:02.48"}]')
                        if records_DB and records_DB is not None:
                            ceEntity.saveBetRecordsToDB(ec, ceEntity.context['gameTypes'], records_DB)
                    except Exception as e:
                        current_app.logger.exception(e)
                        current_app.logger.error('同步%s数据异常 %s至 %s' % (ec, startDate, endDate))
                current_app.logger.info('同步%s交易记录 %s至 %s 结束' % (ec, startDate, endDate))
        except Exception as e:
            current_app.logger.exception(e)
        finally:
            current_app.logger.info('更新redis中的交易记录')
            ecBetsDetailsToRedis(int(time.time())-3600, int(time.time()))