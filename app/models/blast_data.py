from . import db
import json
import decimal, datetime,time
from .data_time import DataTime,LHCDataTime
from app.common.utils import dayLimit
from app.common.numberModal import getModalSQL
import math
from sqlalchemy import text,func,distinct
'''
Created on 2018年8月9日
开奖记录
@author: liuyu
'''

class BlastData(db.Model):
    __tablename__ = 'blast_data'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer);
    number = db.Column(db.String);
    time = db.Column(db.String);
    state = db.Column(db.Integer);
    data = db.Column(db.String);
    
    def getDataSelective(self,args):
        m_sql_c = ' actionNo in '
        m_sql_c = self.createSQL(m_sql_c,args,False)
        m_count = db.session.query(func.count(distinct(BlastBets.actionNo))).filter(text(m_sql_c)).scalar()
        m_sql = '''select actionNo,sum(mode * beiShu * actionNum) betAmount,betType,  
                    sum(bonus) zjAmount,kjTime,lotteryNo from blast_bets
                    where actionNo in '''
        m_sql = self.createSQL(m_sql,args,True)
        m_res = db.session.execute(m_sql)
        m_json = json.loads(json.dumps([dict(r) for r in m_res],ensure_ascii=True,default=alchemyencoder))
        '''
        框架返回格式没有统一
        统一后修改
        '''
        res_json = {}
        res_json['data'] = m_json
        res_json['size'] = m_count
        res_json['pages'] = math.ceil( m_count/ self.pageSize)
        res_json['pageNum'] = self.pageNum
        res_json['pageSize'] = self.pageSize
        res_json['success'] = True
        return res_json
    
    def getDataAndTime(self,args):
        m_cj = {"2019":"2019-02-04","2020":"2020-01-24","2021":"2021-02-11", "2021":"2021-02-11", "2022":"2022-01-31"}
        if args['sActionTime'] is None:
            args['sActionTime'] = time.time()
            #args['stime'] = 1539360000000
        if args['eActionTime'] is None:
            args['eActionTime'] =  args['sActionTime']
        m_day_limit = dayLimit(int(args['sActionTime']), int(args['eActionTime']))
        m_len = len(m_day_limit)
        m_type = args['type']
        m_num = args['page'] - 1
        m_size = args['pageSize']
        m_sql = ''
        m_sql_count = "select count(id) from blast_data_time where type = %s"%(m_type)
        m_count = db.session.query(func.count(DataTime.id)).filter(DataTime.type == m_type).scalar()
        m_count = m_count * m_len
        for index,m_time in enumerate(m_day_limit):
            m_stime = time.localtime(m_time) 
            m_sdate = time.strftime("%Y-%m-%d", m_stime)
            diff = 0;
            if m_type == 9 or m_type == 10:
                cjtime = m_cj[time.strftime("%Y", m_stime)]
                #将年三十转正时间戳
                cjtime = int(time.mktime(time.strptime(cjtime, "%Y-%m-%d")))
                mstime = int(time.mktime(time.strptime(m_sdate, "%Y-%m-%d")))
                diff = (mstime - cjtime)/3600/24
                if diff >= 0 and diff<=6:
                    continue
            m_sql_modal = getModalSQL(m_type,m_sdate,diff)
            m_sql += '''
                select bdt.actionNo,date_format(bdt.actionTime,'%s') kjTime,
                (select data from blast_data where type = %s and number = bdt.actionNo) kjData,
                (select data from blast_data_admin where type = %s and number = bdt.actionNo) ysData,
                (select id from blast_data_admin where type = %s and number = bdt.actionNo) dataAdminID,
                (select sum(mode * beiShu * actionNum) from blast_bets where type = %s and actionNo = bdt.actionNo) betAmount,
                (select sum(bonus) from blast_bets where type = %s and actionNo = bdt.actionNo) zjAmount,
                COALESCE((select state from blast_data where type = %s and number = bdt.actionNo),0) state,
                (select id from blast_data where type = %s and number = bdt.actionNo) dataID
                from (%s ,actionTime,stopTime from blast_data_time where type = %s) bdt 
                '''%(m_sdate + ' ' + '%H:%i:%s',m_type,m_type,m_type,m_type,m_type,m_type,m_type,m_sql_modal,m_type)
            if args['actionNo']:
                    m_sql +=" where  bdt.actionNo = '%s'"%(args['actionNo'])
            if index == m_len - 1:
                m_sql += " order by actionNo desc limit %s,%s"%(m_num*m_size,m_size)
            else:
                m_sql += " UNION ALL "
        #print(m_sql)
        res_json = {}
        res_json['data'] = []
        res_json['total'] = 0
        res_json['pages'] = 0
        res_json['page'] = 0
        res_json['pageSize'] = 0
        res_json['success'] = True
        print(m_sql)
        if m_sql.split() == '':
            return res_json
        
        m_res = db.session.execute(m_sql)
        if args['actionNo']:
            m_count = m_res.rowcount
        m_json = json.loads(json.dumps([dict(r) for r in m_res],ensure_ascii=True,default=alchemyencoder))
        res_json['data'] = m_json
        res_json['total'] = m_count
        res_json['pages'] = math.ceil( m_count/ args['pageSize'])
        res_json['page'] = args['page']
        res_json['pageSize'] = m_res.rowcount
        res_json['success'] = True
        return res_json

    def getLHCDataAndTime(self,args):
        if args['sActionTime'] is None:
            args['sActionTime'] = time.time()
            #args['stime'] = 1539360000000
        if args['eActionTime'] is None:
            args['eActionTime'] = time.time()
        #m_sActionTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(args['sActionTime']))
        #m_eActionTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(args['eActionTime']))
        m_sActionTime = time.strftime("%Y-%m-%d 00:00:00",time.localtime(args['sActionTime']))
        m_eActionTime = time.strftime("%Y-%m-%d 23:59:59",time.localtime(args['eActionTime']))
        m_type = args['type']
        m_num = args['page'] - 1
        m_size = args['pageSize']
        m_sql = ''
        m_count = db.session.query(func.count(LHCDataTime.id)).filter(LHCDataTime.actionTime>=m_sActionTime,LHCDataTime.actionTime<=m_sActionTime).scalar()
        m_sql += '''
            select bdt.actionNo,date_format(bdt.actionTime,'%s') kjTime,
            (select data from blast_data where type = 34 and number = bdt.actionNo) kjData,
            (select data from blast_data_admin where type = 34 and number = bdt.actionNo) ysData,
            (select id from blast_data_admin where type = 34 and number = bdt.actionNo) dataAdminID,
            (select sum(mode * beiShu * actionNum) from blast_bets where type = 34 and actionNo = bdt.actionNo) betAmount,
            (select sum(bonus) from blast_bets where type = 34 and actionNo = bdt.actionNo) zjAmount,
            COALESCE((select state from blast_data where type = 34 and number = bdt.actionNo),0) state,
            (select id from blast_data where type = 34 and number = bdt.actionNo) dataID,
            bdt.actionTime
            from (select CONCAT(date_format(actionTime,'%s-'),substring((10000+actionNo),2)) actionNo,actionTime from blast_lhc_time where type = 34) bdt 
            where bdt.actionTime >='%s' and bdt.actionTime <='%s'
            '''%('%Y-%m-%d %H:%i:%s','%Y',m_sActionTime,m_eActionTime)
        if args['actionNo']:
                m_sql +=" and  bdt.actionNo = '%s'"%(args['actionNo'])
        m_sql += " order by bdt.actionNo desc limit %s,%s"%(m_num*m_size,m_size)
        m_res = db.session.execute(m_sql)
        if args['actionNo']:
            m_count = m_res.rowcount
        m_json = json.loads(json.dumps([dict(r) for r in m_res],ensure_ascii=True,default=alchemyencoder))
        res_json = {}
        res_json['data'] = m_json
        res_json['total'] = m_count
        res_json['pages'] = math.ceil( m_count/ args['pageSize'])
        res_json['page'] = args['page']
        res_json['pageSize'] = m_res.rowcount
        res_json['success'] = True
        return res_json
        
    
    
    def createSQL(self,sqlstr,args,sqltype):
        sqlstr += '(select number from blast_data '
        if('type' in args and args['type'] is not None):
            sqlstr += ' where type = %s' %(args['type'])
        if('stime' in args and args['stime'] is not None):
            sqlstr += ' and time >= %s' %(int(args['stime']/1000))
        if('etime' in args and args['etime'] is not None):
            sqlstr += ' and time <= %s' %(int(args['etime']/1000))
        if('actionNo' in args and args['actionNo'] is not None):
            sqlstr += " and number =  '%s' " %(args['actionNo'])
        sqlstr += ') '
        if('pageNum' in args and args['pageNum'] is not None):
            self.pageNum = args['pageNum']
        if('pageSize' in args and args['pageSize'] is not None):
            self.pageSize = args['pageSize']
        if(sqltype):
            sqlstr += 'group by actionNo order by kjTime'
            m_num = self.pageNum - 1
            sqlstr += ' limit %s,%s'%(m_num*self.pageSize,self.pageSize)
        return sqlstr

def alchemyencoder(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)