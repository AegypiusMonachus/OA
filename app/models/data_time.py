from flask import current_app

from . import db
from sqlalchemy.orm import relationship,class_mapper
from .blast_played_group import BlastPlayedGroup
import json

'''
Created on 2018年8月9日
开奖时间表
@author: liuyu
'''

class DataTime(db.Model):
    __tablename__ = 'blast_data_time'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    actionNo = db.Column(db.String)
    actionTime = db.Column(db.String)
    stopTime = db.Column(db.String)
    
    
    '''     
    根据彩票得类型查询当前得期号
    '''
    @staticmethod
    def getData(type,time):
        m_res = db.session.query(DataTime).filter(DataTime.type == type,DataTime.actionTime>=time).order_by(DataTime.actionNo).first()
        return m_res

class LHCDataTime(db.Model):
    __tablename__ = 'blast_lhc_time'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    actionNo = db.Column(db.String)
    actionTime = db.Column(db.String)