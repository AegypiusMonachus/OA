# 检视娱乐城操作历史记录
from app.models import db


class OperationalRecord(db.Model):
    __tablename__ = 'tb_entertainment_city_operational_record'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    creatTime = db.Column(db.Integer)
    remark = db.Column(db.String)
    ylc = db.Column(db.String)


# 会员详细资料---检视所有钱包
class YlcOutstationBalance(db.Model):
    __tablename__ = 'tb_entertainment_city_outstation_balance'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    uid = db.Column(db.Integer)
    jsonlist = db.Column(db.String)
    allbalance = db.Column(db.String)
