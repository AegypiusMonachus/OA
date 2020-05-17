from flask import current_app
from flask_restful import abort
from . import db
from sqlalchemy.orm import relationship,class_mapper
from .blast_played_group import BlastPlayedGroup
import json
import decimal, datetime,time
from app.models.common.utils import paginate
'''
Created on 2018年8月9日
彩票类型
@author: liuyu
'''

class BlastType(db.Model):
    __tablename__ = 'blast_type'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer)
    enable = db.Column(db.Integer)
    isDelete = db.Column(db.Integer)
    sort = db.Column(db.Integer)
    name = db.Column(db.String)
    codeList = db.Column(db.String)
    title = db.Column(db.String)
    data_ftime = db.Column(db.Integer)
    defaultViewGroup = db.Column(db.Integer)
    android = db.Column(db.Integer)
    num = db.Column(db.Integer)
    group = db.Column(db.Integer)

    
    def getDataType(self ,page, pageSize, criterion):
        m_query = db.session.query(BlastType)
        pagination = paginate(m_query, criterion, page, pageSize)
        return pagination
    
    @staticmethod
    def update(id, **args):
        m_parm = {key: args[key] for key in args if args[key] is not None}
        try:
            m_res = BlastType.query.filter(BlastType.id == id).update(m_parm)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return m_res
    '''
        查询所有彩票和彩票的玩法
    '''
    def getPlayedGroup(self):
        self.playedGroup = BlastPlayedGroup.query.filter(BlastPlayedGroup.type == self.type).order_by(BlastPlayedGroup.sort).all()
        
    '''    
    def getTypeAndPlayedGroup(self):
        m_res = db.session.query(BlastType).all()
        m_bt_list =[];
        for m_bt in m_res:
            m_type = m_bt.type
            m_res_pg = BlastPlayedGroup.query.filter(BlastPlayedGroup.type == m_type).all()
            for m_pg in m_res_pg:
                m_bt.playedgroup.append(self.as_dict(m_pg))
                print(self.as_dict(m_pg))
            m_bt_list.append(m_bt)
        return m_bt_list
    '''
    @staticmethod
    def getDic():
        m_sql = ''' select tlt.dic_code, bt.id id, bt.title title, bt.name name, bt.type type 
                    from tb_lottery_type tlt , blast_type bt 
                    where tlt.blast_type_id = bt.id 
                '''
        m_res = db.session.execute(m_sql)
        m_json = json.loads(json.dumps([dict(r) for r in m_res],ensure_ascii=True,default=BlastType.alchemyencoder))
        return m_json
    
    @staticmethod
    def alchemyencoder(obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        
        
