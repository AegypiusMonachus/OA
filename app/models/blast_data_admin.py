from flask import current_app
from flask_restful import abort
from . import db
from sqlalchemy import func,desc
from .blast_data import BlastData
from app.models.common.utils import paginate
import time
from app.common.utils import kaijiang 
'''
Created on 2018年8月9日
自主彩
@author: liuyu
'''
class BlastDataAdmin(db.Model):
    __tablename__ = 'blast_data_admin'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer)
    time = db.Column(db.Integer)
    actionNo = db.Column('number',db.String)
    data = db.Column(db.String)
    uid = db.Column(db.Integer)
    username = db.Column(db.String)
    
    '''     
    系统彩查询
    '''
    def getBlastDataAdmin(self,criterion,page,pageSize):
        m_query = db.session.query(BlastDataAdmin).order_by(desc(BlastDataAdmin.actionNo))
        pagination = paginate(m_query, criterion, page, pageSize)
        return pagination
    '''
    根据彩票类型获取开奖信息
    '''
    @staticmethod
    def getData(id,page_num,item_num):
        if type:
            page = db.session.query(BlastDataAdmin).filter(BlastDataAdmin.type == id).order_by(BlastDataAdmin.actionNo).paginate(page_num, item_num, error_out=False)
        else:
            return None
        while not page.items and page.has_prev:
            page = page.prev()
        return page 
    
    '''
    根据彩票类型获取开奖信息
    '''
    def update(self, id, kwargs):
        #m_res = db.session.query(BlastData.status).filter(BlastData.type == kwargs['type'],BlastData.number == kwargs['number']).first();
        #print(m_res == 1)
        #args = {key: kwargs[key] for key in kwargs if kwargs[key] is not None}
#         args = {"data":kwargs['data']}
#         try:
#             m_res = BlastData.query.filter(BlastData.type == kwargs['type'],BlastData.number == kwargs['actionNo']).first()
#             if m_res:
#                 if m_res.state == 1 or m_res.state == 99:
#                     m_dao = db.session.execute("call pro_rollbackKJ('%s',%s);"%(kwargs['actionNo'],kwargs['type']))
#                     m_res = kaijiang(kwargs)
#                     if 'errorCode' in m_res:
#                         return{'success': False,"error_code":1020,"error_message":"更新失败"}
#                     #BlastData.query.filter(BlastData.type == kwargs['type'],BlastData.number == kwargs['actionNo']).update(args);
#                     BlastData.query.filter(BlastData.type == kwargs['type'],BlastData.number == kwargs['actionNo']).update({"state":1,"data":args['data']})
#             BlastDataAdmin.query.filter(BlastDataAdmin.actionNo == kwargs['actionNo'],BlastDataAdmin.type == kwargs['type']).update(args)
#             db.session.commit()
#         except:
#             db.session.rollback()
#             try:
#                 if m_res.state == 1 or m_res.state == 99:
#                     BlastData.query.filter(BlastData.type == kwargs['type'],BlastData.number == kwargs['actionNo']).update({"state":99})
#                     db.session.commit()
#             except:
#                 db.session.rollback()
#                 db.session.remove()
#                 abort(500)
#             return{'success': False,"error_code":1020,"error_message":"更新失败"}
        return {'success': True}
    
    '''
    根据彩票类型获取开奖信息
    
    @staticmethod
    def insert(kwargs):
        m_dataAdmin = BlastDataAdmin();
        m_dataAdmin.time = int(kwargs['time']/1000);
        m_dataAdmin.data = kwargs['data'];
        m_dataAdmin.type = kwargs['type'];
        m_dataAdmin.uid = 999
        m_dataAdmin.username = 'admin'
        m_localTime = time.localtime(m_dataAdmin.time);
        m_data = time.strftime("%Y%m%d", m_localTime) 
        #根据类型和时间获取开奖期号 1536554338 = 12:38
        m_dataTime = DataTime.getData(kwargs['type'], m_localTime)
        m_number = "%s-%s"%(m_data,m_dataTime.actionNo)
        m_count = db.session.query(func.count(BlastDataAdmin.id)).filter(BlastDataAdmin.number == m_number).scalar()
        if m_count != 0:
            abort(500)
        m_dataAdmin.number = m_number
        try:
            db.session.add(m_dataAdmin)
            db.session.commit()
        except:
            db.session.rollback()
            abort(500)
        return m_dataAdmin 
    '''
   
    '''
    根据彩票类型获取开奖信息
    '''
    def insert(self,kwargs):
        #m_count = db.session.query(func.count(BlastDataAdmin.id)).filter(BlastDataAdmin.type == kwargs['type'],BlastDataAdmin.actionNo == kwargs['actionNo']).scalar()
        m_dataAdmin = None
        try:
            m_dataAdmin = BlastDataAdmin.query.filter(BlastDataAdmin.type == kwargs['type'],BlastDataAdmin.actionNo == kwargs['actionNo']).first()
            if m_dataAdmin is not None:
                BlastDataAdmin.query.filter(BlastDataAdmin.type == kwargs['type'],BlastDataAdmin.actionNo == kwargs['actionNo']).update({"data":kwargs['data']})
                m_dataAdmin.data = kwargs['type']
            else:
                m_dataAdmin = BlastDataAdmin();
                m_dataAdmin.time = int(time.time());
                m_dataAdmin.data = kwargs['data'];
                m_dataAdmin.type = kwargs['type'];
                m_dataAdmin.actionNo = kwargs['actionNo'];
                m_dataAdmin.uid = 999
                m_dataAdmin.username = 'admin'
                db.session.add(m_dataAdmin)
                db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return m_dataAdmin 
   
   
    def delete(self,id):
        m_dao = BlastDataAdmin.query.filter(BlastDataAdmin.id == id).first()
        if m_dao:
            try:
                db.session.delete(m_dao)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.remove()
                abort(500)
        return 1
    
    def rollBack(self,number,type):
        m_dao = db.session.execute("call pro_rollbackKJ('%s',%s);"%(number,type))
        return True
