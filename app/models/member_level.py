from flask_restful import abort
from . import db
from .member import Member
from .common.utils import execute
from app.models.common.utils import *

'''
Created on 2018年8月9日
彩票类型
@author: liuyu
'''
class MemberLevel(db.Model):
    __tablename__ = 'blast_member_level'

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    level = db.Column(db.Integer)
    levelName = db.Column(db.String)
    min_rk = db.Column(db.Float)
    max_rk = db.Column(db.Float)
    min_tk = db.Column(db.Float)
    max_tk = db.Column(db.Float)
    sx_Free = db.Column(db.Float)
    mcfy = db.Column(db.Integer)
    tksc = db.Column(db.Integer)
    ms = db.Column(db.Integer)
    js = db.Column(db.Integer)
    dkzfsxf = db.Column(db.String)
    gsrkyh = db.Column(db.String)
    xszfyh = db.Column(db.String)
    zcscj = db.Column(db.String)
    kscz = db.Column(db.String)
    ckjhb = db.Column(db.String)
    xz_Free = db.Column(db.Float)
    zfbmqckzt = db.Column(db.Integer)
    remark = db.Column(db.String)
    danger = db.Column(db.String)
    isBanned = db.Column(db.Integer,default = 1)

    members_with_level_config = db.relationship(
		'Member', foreign_keys=[Member.levelConfig], backref='level_config', lazy='dynamic')
    members_with_default_level_config = db.relationship(
		'Member', foreign_keys=[Member.defaultLevelConfig], backref='default_level_config', lazy='dynamic')

    '''
    查询会员等级
    '''
    def getData(self, criterion, page, pageSize):
        m_query = db.session.query(MemberLevel)
        pagination = paginate(m_query, criterion, page, pageSize)
        return pagination
        # m_sql = 'select *,(select count(uid) from blast_members where grade = id) memberCount from blast_member_level '
        # if id:
        #     m_sql += 'where id = %s order by id' %(id)
        # m_result = execute(m_sql, page, pageSize)
        # return m_result
    
    def update(self, id, **args):
        # m_parm = {key: args[key] for key in args if args[key] is not None}
        try:
            m_res = MemberLevel.query.filter(MemberLevel.id == id).update(args)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return m_res

    def insert(self,**args):
        dao = MemberLevel(**args)
        try:
            db.session.add(dao)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return dao

    def delete(self,id):
        m_dao = MemberLevel.query.filter(MemberLevel.id == id).first()
        if m_dao:
            try:
                db.session.delete(m_dao)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.remove()
                abort(500)
        return 1

    def getLevels(self):
        m_dao = db.session.query(MemberLevel.id,MemberLevel.levelName).all()
        return m_dao

