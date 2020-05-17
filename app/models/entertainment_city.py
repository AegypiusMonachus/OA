from . import db

class EntertainmentCity_password(db.Model):
    __tablename__ = 'tb_entertainment_city_private_info'
    code = db.Column(db.String, primary_key=True)
    merchantCode = db.Column(db.String)
    token = db.Column(db.String)
    key = db.Column(db.String)
    hash = db.Column(db.String)

class EntertainmentCity(db.Model):
    __tablename__ = 'tb_entertainment_city'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String)
    name = db.Column(db.String)
    game_types = db.Column(db.String)
    apidomain = db.Column(db.String)
    extension = db.Column(db.String)
    enable = db.Column(db.Integer)
    qz = db.Column(db.String)
    gameList = db.Column(db.String)
    experience = db.Column(db.Integer)
    '''
    娱乐城首页数据获取
    '''
    def getList(self):
        m_list = db.session.query(EntertainmentCity).filter().all()
        return m_list
    '''
        根据游戏平台提供的游戏类型获取游戏数据
    '''
    def getEC(self):
        m_list = db.session.query(
                EntertainmentCity.code,EntertainmentCity.name,EntertainmentCity.game_types,
                EntertainmentCity.experience).filter(EntertainmentCity.enable == 1)
        return self.groupEc(m_list)
    
    def getGameData(self,gameType):
        m_sql = '''select code from tb_entertainment_city 
                    where FIND_IN_SET(%s,game_type) >0 and enable = 1
                '''%(gameType) 
        m_res = db.session.execute(m_sql)
        print(m_res)
    
    '''
        获取游戏平台基本数据接口
        这个接口为游戏平台接口调用提供数据
    '''
    def getDataByCode(self,ecCode):
        dao = db.session.query(EntertainmentCity).filter(EntertainmentCity.code ==ecCode).first()
        dao_key = db.session.query(EntertainmentCity_password).filter(EntertainmentCity_password.code == ecCode).first()
        if dao is None:
            return None
        data = {};
        data['code'] = dao.code
        data['name'] = dao.name
        data['apidomain'] = dao.apidomain
        data['merchantCode'] = dao_key.merchantCode
        data['token'] = dao_key.token
        data['key']   = dao_key.key
        data['extension'] = dao.extension
        data['hash'] = dao_key.hash
        data['gameList'] = dao.gameList
        data['gameTypes'] = dao.game_types
        data['qz'] = dao.qz
        return data;
    
    def groupEc(self,ecList):
        gameMap = {"1001":None,"1002":None,"1003":None,"1004":None,"1005":None,"1006":None,"1007":None}
        for key in gameMap:
            for ec in ecList:
                if key in ec.game_types:
                    if gameMap[key] is None:
                        gameMap[key] = [{"code":ec.code,"name":ec.name,"experience":ec.experience}]
                    else:
                        gameMap[key].append({"code":ec.code,"name":ec.name,"experience":ec.experience})
        return gameMap

    def getListAll(self):
        m_list = db.session.query(EntertainmentCity.code, EntertainmentCity.game_types).all()
        return m_list

class EntertainmentCity_get_qb(db.Model):
    __tablename__ = 'tb_entertainment_city_getback_qb'
    id = db.Column(db.Integer, primary_key=True)
    ec = db.Column(db.String)
    username = db.Column(db.String)#操作人员
    actiontime = db.Column(db.Integer)
    log_json = db.Column(db.String)



