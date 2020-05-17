from . import db
from app.models.common.utils import *
from flask_restful import abort


class ConfigYongjin(db.Model):
    __tablename__ = 'tb_config_yongjin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    zdtze = db.Column(db.Float)
    dbcksxf = db.Column(db.Float)
    cksxfsx = db.Column(db.Float)
    dbqksxf = db.Column(db.Float)
    qksxfsx = db.Column(db.Float)
    zdckje = db.Column(db.Float)
    enable = db.Column(db.Integer)

    members = db.relationship('Member', backref='commission_config', lazy='dynamic')

    def getData(self, criterion, pageNum, pageSize):
        m_query = db.session.query(ConfigYongjin)
        page = paginate(criterion=criterion, query=m_query, page=pageNum, per_page=pageSize)
        # page = db.session.query(SysadminBank).paginate(1, 20, error_out=False)
        while not page.items and page.has_prev:
            page = page.prev()
        if not page.items:
            return None
        return page

    def update(self, id, **args):
        m_parm = {key: args[key] for key in args if args[key] is not None}
        try:
            m_res = ConfigYongjin.query.filter(ConfigYongjin.id == id).update(m_parm)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return m_res

    def insert(self, **args):
        dao = ConfigYongjin(**args)
        try:
            db.session.add(dao)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return dao

    def delete(self, id):
        m_dao = ConfigYongjin.query.filter(ConfigYongjin.id == id).first()
        if m_dao:
            try:
                db.session.delete(m_dao)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.remove()
                abort(500)
        return 1


""""""


class YongJinTyb(db.Model):
    __tablename__ = 'tb_config_yongjin_tyb'
    id = db.Column(db.Integer, primary_key=True)
    Yid = db.Column(db.Integer)
    pcJine = db.Column(db.Float())
    yxhuiyuan = db.Column(db.Integer)
    youhui = db.Column(db.Float())
    fanshui = db.Column(db.Float())
    tuiyongbi = db.Column(db.String)
