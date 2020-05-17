from . import db


'''
Created on 2018年8月9日
字典表
@author: liuyu
'''

class Dictionary(db.Model):
    __tablename__ = 'tb_dic'
    code = db.Column('code', db.Integer, primary_key=True)
    type = db.Column('type', db.Integer, primary_key=True)
    name = db.Column('name', db.String, primary_key=True)
    remark = db.Column('remark', db.String, primary_key=True)
    
    
    '''     
    根据类型获取所有数据
    '''
    @staticmethod
    def getDataByType(type):
        if id:
            return db.session.query(Dictionary).filter(Dictionary.type == type).all()
        else:
            return db.session.query(Dictionary).all()