'''
Created on 2019
娱乐城
@author: liuyu
'''
from flask_restful import Resource
from app.entertainmentcity import EntertainmentCityFactory
from flask_restful.reqparse import RequestParser
from flask import g
from app.common.orderUtils import createECOrderId
from app.models.entertainment_city import EntertainmentCity

'''
娱乐城接口
'''
class EntertainmentCityAPI(Resource):
    def get(self):
        m_data = EntertainmentCity().getEC()
        return {"success": True,"data":m_data};
    
'''
娱乐城游戏
'''
class GameListAPI(Resource):
    def get(self,code):
        ce = EntertainmentCityFactory.getEntertainmentCity(code);
        m_data = ce.gameList(1)
        return m_data;
    
    
    
    