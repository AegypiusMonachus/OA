from . import db
from app.models.common.utils import *
from flask_restful import abort
from app.redis.redisConnectionManager import IPRedisManager

'''
系统设置-ip白名单
'''

class ConfigIplist(db.Model):
    __tablename__ = 'tb_config_iplist'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String)
    state = db.Column(db.Integer)
    uid = db.Column(db.Integer)
    strTime = db.Column(db.String)

    # 数据库查询
    def getDate(self,criterion,page,pagesize):
        m_query = db.session.query(ConfigIplist)
        pagination = paginate(m_query,criterion,page,pagesize)
        return pagination

    # 数据库插入
    def insert(self,**kwargs):
        dao = ConfigIplist(**kwargs)
        try:
            db.session.add(dao)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return dao

    # 数据库更改
    def update(self, id, **args):
        m_parm = {key: args[key] for key in args if args[key] is not None}
        try:
            ConfigIplist.query.filter(ConfigIplist.id == id).update(m_parm)
            m_res = ConfigIplist.query.filter(ConfigIplist.id == id).all()
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return m_res

    # 数据库的删除
    def delete(self, id):
        m_dao = ConfigIplist.query.filter(ConfigIplist.id == id).first()

        if m_dao:
            try:
                db.session.delete(m_dao)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.remove()
                abort(500)
        return 1

    # 获取要删除的IP数据
    def getIpToDelete(self, id):
        m_query = db.session.query(ConfigIplist).get(id)
        return m_query

    def getIpToUpdate(self):
        m_query = db.session.query(ConfigIplist).all()
        return m_query

    # 服务器初始化存入redis
    @staticmethod
    def getDataToRedis():

        with IPRedisManager.app.app_context():
            redisImpl = IPRedisManager.get_redisImpl()
            redisImpl.flushdb()
            m_query = db.session.query(ConfigIplist).all()

            for i in m_query:
                ip = i.ip
                redisImpl.hset(name="IPList",key=ip,value="")
            # print(redisImpl.hgetall('IPList'))


