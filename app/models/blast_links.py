from . import db
from flask import abort
from app.common.utils import *
from sqlalchemy import func


'''
Created on 2018年8月9日
推广链接
@author: liuyu
'''

class BlastLinks(db.Model):
    __tablename__ = 'blast_links'
    lid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    enable = db.Column(db.Integer)
    uid = db.Column(db.Integer)
    type = db.Column(db.Integer)
    regIP = db.Column(db.Integer)
    regTime = db.Column(db.Integer)
    updateTime = db.Column(db.Integer)
    fanDian = db.Column(db.Numeric(3,1))
    link = db.Column(db.String)
    
    def getData(self,criterion):
        page = db.session.query(BlastLinks).filter(*criterion).paginate(1, 50, error_out=False)
        while not page.items and page.has_prev:
            page = page.prev()
        if not page.items:
            return None
        return page
    
    def insert(self,**kwargs):
        m_count = db.session.query(func.count(BlastLinks.lid)).filter(BlastLinks.uid == kwargs['uid']).scalar()
        if m_count > 10:
            abort(404)        
        dao = BlastLinks(**kwargs)
        try:
            db.session.add(dao)
            db.session.commit()
            #根据Lid生成推广链接码，在更新回数据库
            m_link = str_to_hex(myxor(str(dao.lid),None))
            m_parm ={}
            m_parm["link"] = m_link
            m_res = BlastLinks.query.filter(BlastLinks.lid == dao.lid).update(m_parm)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return dao 
    
    def update(self,id,kwargs):
        m_parm = {key: kwargs[key] for key in kwargs if kwargs[key] is not None}
        try:
            m_res = BlastLinks.query.filter(BlastLinks.lid == id).update(m_parm)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return m_res

    def delete(self,id):
        m_dao = BlastLinks.query.filter(BlastLinks.lid == id).first()
        if m_dao:
            try:
                db.session.delete(m_dao)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.remove()
                abort(500)
        return 1


class LinksUser(db.Model):
    __tablename__ = 'tb_links_user'
    lid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    enable = db.Column(db.Integer)
    uid = db.Column(db.Integer)
    fanDian = db.Column(db.Numeric(4,1))
    domain = db.Column(db.String)
    web_domain = db.Column(db.String)
    mobile_domain = db.Column(db.String)
    
    def getData(self,criterion):
        page = db.session.query(LinksUser).filter(*criterion).paginate(1, 50, error_out=False)
        while not page.items and page.has_prev:
            page = page.prev()
        if not page.items:
            return None
        return page
    
    def insert(self,**kwargs):
        dao = LinksUser(**kwargs)
        try:
            db.session.add(dao)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return dao 
    
    def update(self,id,kwargs):
        m_parm = {key: kwargs[key] for key in kwargs if kwargs[key] is not None}
        try:
            m_res = LinksUser.query.filter(LinksUser.lid == id).update(m_parm)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return m_res

    def delete(self,id):
        m_dao = LinksUser.query.filter(LinksUser.lid == id).first()
        if m_dao:
            try:
                db.session.delete(m_dao)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.remove()
                abort(500)
        return 1