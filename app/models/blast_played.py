
from . import db
from flask_restful import abort
from app.models.common.utils import paginate
'''
Created on 2018年8月9日
彩票类型
@author: liuyu
'''
class BlastPlayed(db.Model):
    __tablename__ = 'blast_played'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Integer)
    enable = db.Column(db.Integer)
    type = db.Column(db.Integer())
    bonusProp = db.Column(db.Numeric(10,3))
    bonusPropBase = db.Column(db.Numeric(10,3))
    selectNum = db.Column(db.Integer())
    groupId = db.Column(db.Integer())
    simpleInfo = db.Column(db.String)
    info = db.Column(db.String)
    example = db.Column(db.String)
    android = db.Column(db.String)
    sort = db.Column(db.String)
    minCharge = db.Column(db.String)
    allCount = db.Column(db.String)
    maxCount = db.Column(db.String)
    maxCharge = db.Column(db.String)
    '''
    根据type查询所有玩法
    '''
    def getPlayedByGroupId(self,criterion,page,pageSize):
        m_query = db.session.query(BlastPlayed)
        pagination = paginate(m_query, criterion, page, pageSize)
        return pagination
    
    
    def update(self,groupId,**m_args):
        try:
            model = m_args['model']
            if model == 1:
                argsList = m_args['data']
                for args in argsList:
                    id = args['id']
                    del args['id']
                    m_parm = {key: args[key] for key in args if args[key] is not None}
                    m_res = BlastPlayed.query.filter(BlastPlayed.id == id).update(m_parm)
            elif model == 2:
                m_Change = m_args['charge']
                m_parm = {'maxCharge':m_Change}
                m_res = BlastPlayed.query.filter(BlastPlayed.groupId == groupId).update(m_parm)
            elif model == 3:
                m_Change = m_args['charge']
                m_parm = {'minCharge':m_Change}
                m_res = BlastPlayed.query.filter(BlastPlayed.groupId == groupId).update(m_parm)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return 1


class BlastPlayedCredit(db.Model):
    __tablename__ = 'blast_played_xinyong'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Integer)
    enable = db.Column(db.Integer)
    type = db.Column(db.Integer())
    bonusProp = db.Column(db.Numeric(10, 3))
    groupId = db.Column(db.Integer())
    remark = db.Column(db.String())
    ruleName = db.Column(db.String())
    sort = db.Column(db.String)
    minCharge = db.Column(db.String)
    allCount = db.Column(db.String)
    maxCount = db.Column(db.String)
    maxCharge = db.Column(db.String)
    '''
    根据type查询所有玩法
    '''

    def getPlayedByGroupId(self, criterion, page, pageSize):
        m_query = db.session.query(BlastPlayedCredit)
        pagination = paginate(m_query, criterion, page, pageSize)
        return pagination
    def update(self, groupId, **m_args):
        try:
            model = m_args['model']
            if model == 1:
                argsList = m_args['data']
                for args in argsList:
                    id = args['id']
                    del args['id']
                    m_parm = {key: args[key] for key in args if args[key] is not None}
                    m_res = BlastPlayedCredit.query.filter(BlastPlayedCredit.id == id).update(m_parm)
            elif model == 2:
                m_Change = m_args['charge']
                m_parm = {'maxCharge': m_Change}
                m_res = BlastPlayedCredit.query.filter(BlastPlayedCredit.groupId == groupId).update(m_parm)
            elif model == 3:
                m_Change = m_args['charge']
                m_parm = {'minCharge': m_Change}
                m_res = BlastPlayedCredit.query.filter(BlastPlayedCredit.groupId == groupId).update(m_parm)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return 1