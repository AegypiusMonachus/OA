import time,pytz,datetime,requests,hashlib,json
from app.models.entertainment_city import EntertainmentCity
# from app.entertainmentcity import EntertainmentCityFactory
# from app.entertainmentcity import scheduler
import json
from app.models import *
from flask import current_app
from app.common.utils import strToBase64str
from app.common.orderUtils import createECOrderId
#from .transfer import Transfer

def getName_all_list():
    # m_results = EntertainmentCity.query(EntertainmentCity.code).filter(EntertainmentCity.enable == 1).all()
    # m_results = ['AG','PT','KAIYUAN']
    m_results = []
    m_query = db.session.query(EntertainmentCity.code).filter(EntertainmentCity.enable == 1).all()
    for names in m_query:
        m_results.append(names[0])
    get_bet_all = {}
    for names_one in m_results:
        get_bet_all['%s' % (names_one)] = []
    # print(get_bet_all)
    return get_bet_all
a = []
def getName_all_list_two(get_bet_all=None):
    if get_bet_all != None and get_bet_all not in a:
        a.append(get_bet_all)
    return a

def getName_all_list_two_all(get_bet_all):
    print('成功进入getName_all_list_two')
    print(get_bet_all)
    return get_bet_all

