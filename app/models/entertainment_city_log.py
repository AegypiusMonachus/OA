from . import db
from sqlalchemy import func

'''
记录娱乐城登录的日志表
与账变信息表不同，他只记录时间，会员，娱乐城和金额
'''
class EntertainmentCityLog(db.Model):
    __tablename__ = 'tb_entertainment_city_log'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    username = db.Column(db.String)
    ec = db.Column(db.String)
    actionTime = db.Column(db.Integer)
    ip = db.Column(db.Integer)
    def getLastLogin(self,uid):
        m_res = db.session.query(EntertainmentCityLog.ec).filter(EntertainmentCityLog.uid == uid).order_by(EntertainmentCityLog.actionTime.desc()).first()
        if m_res:
            return m_res[0]
        else:
            return None
    def insert(self,**kwargs):
        dao = EntertainmentCityLog(**kwargs)
        try:
            db.session.add(dao)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
    
        
    
'''
记录娱乐城登录的日志表
与账变信息表不同，他只记录时间，会员，娱乐城和金额
'''
class EntertainmentCityTradeLog(db.Model):
    __tablename__ = 'tb_entertainment_city_trade_log'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    username = db.Column(db.String)
    ec = db.Column(db.String)
    last_ec = db.Column(db.String)
    actionTime = db.Column(db.Integer)
    ip = db.Column(db.Integer)
    orderid = db.Column(db.String)
    operator = db.Column(db.String)
    wjorderId = db.Column(db.String)
    amount = db.Column(db.Float)
    state = db.Column(db.Integer)
    remark = db.Column(db.String)
    type = db.Column(db.Integer)
    real_ip = db.Column(db.String)
    main_confirm = db.Column(db.Integer)
    ec_confirm = db.Column(db.Integer)
    is_automatic = db.Column(db.Integer)
    # status = db.Column(db.Integer)
    def insert(self,**kwargs):
        dao = EntertainmentCityTradeLog(**kwargs)
        try:
            db.session.add(dao)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
        return dao
            
class EntertainmentCityTradeDetail(db.Model):
    __tablename__ = 'tb_entertainment_city_trade_detail_log'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    username  = db.Column(db.String)
    ec = db.Column(db.String)
    actionTime = db.Column(db.Integer)
    orderid = db.Column(db.String)
    amount = db.Column(db.Float)
    state = db.Column(db.Integer)
    remark = db.Column(db.String)
    type = db.Column(db.Integer)
    info = db.Column(db.String)
    
    def insert(self,**kwargs):
        dao = EntertainmentCityTradeDetail(**kwargs)
        try:
            db.session.add(dao)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()