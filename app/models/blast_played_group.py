from flask import current_app

from . import db
from flask_restful import abort
from app.models.common.utils import paginate
'''
Created on 2018年8月9日
彩票类型
@author: liuyu
'''

class BlastPlayedGroup(db.Model):
    __tablename__ = 'blast_played_group'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    type = db.Column('type', db.Integer())
    enable = db.Column('enable', db.Integer())
    groupName = db.Column('groupName',db.String)
    sort = db.Column('sort', db.Integer())
    bdwEnable = db.Column('bdwEnable', db.Integer())
    android = db.Column('android', db.Integer())
    
    '''     
    根据类型获取所有数据
    '''
    def getPlayedByType(self,criterion,page,pageSize):
        m_query = db.session.query(BlastPlayedGroup)
        pagination = paginate(m_query, criterion, page, pageSize)
        return pagination
    
    def update(self,id, args):
        m_parm = {key: args[key] for key in args if args[key] is not None}
        try:
            m_res = BlastPlayedGroup.query.filter(BlastPlayedGroup.id == id).update(m_parm)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return m_res


class BlastPlayedGroupCredit(db.Model):
    '''
    信用玩法
    '''
    __tablename__ = 'blast_played_group_xinyong'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    type = db.Column('type', db.Integer())
    enable = db.Column('enable', db.Integer())
    groupName = db.Column('groupName', db.String)
    sort = db.Column('sort', db.Integer())
    typename = db.Column('typename', db.String())

    '''     
    根据类型获取所有数据
    '''

    def getPlayedByType(self, criterion, page, pageSize):
        m_query = db.session.query(BlastPlayedGroupCredit)
        pagination = paginate(m_query, criterion, page, pageSize)
        return pagination

    def update(self, id, args):
        m_parm = {key: args[key] for key in args if args[key] is not None}
        try:
            m_res = BlastPlayedGroupCredit.query.filter(BlastPlayedGroupCredit.id == id).update(m_parm)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return m_res
