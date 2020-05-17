from flask import current_app

from . import db
import json
from flask_restful import abort
from app.models.common.utils import paginate
'''
Created on 2018年8月9日
六合彩赔率设置和玩法小类
@author: liuyu
'''

class BlastLHCRatio(db.Model):
    __tablename__ = 'blast_lhc_ratio'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    bonusProp = db.Column('Rte', db.Integer())
    enable = db.Column(db.Integer())
    name = db.Column('rName',db.String)
    sort = db.Column(db.Integer())
    android = db.Column(db.Integer())
    minCharge = db.Column(db.Integer())
    maxCharge = db.Column(db.Integer())
    playid = db.Column(db.Integer())
    
    def getData(self,criterion, page, pageSize):
        m_query = db.session.query(BlastLHCRatio)
        pagination = paginate(m_query, criterion, page, pageSize)
        return pagination  
     
    '''
        更新
    '''
    def update(self,playeid, **m_args):
        model = m_args['model']
        try:
            model = m_args['model']
            if model == 1:
                argsList = m_args['data']
                for args in argsList:
                    id = args['id']
                    del args['id']
                    m_parm = {key: args[key] for key in args if args[key] is not None}
                    m_res = BlastLHCRatio.query.filter(BlastLHCRatio.id == id).update(m_parm)
            elif model == 2:
                m_Change = m_args['charge']
                m_parm = {'maxCharge':m_Change}
                m_res = BlastLHCRatio.query.filter(BlastLHCRatio.playid == playeid).update(m_parm)
            elif model == 3:
                m_Change = m_args['charge']
                m_parm = {'minCharge':m_Change}
                m_res = BlastLHCRatio.query.filter(BlastLHCRatio.playid == playeid).update(m_parm)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return 1
