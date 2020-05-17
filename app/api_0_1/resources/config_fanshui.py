from flask import request
from flask_restful import Resource, marshal_with, fields
from flask_restful.reqparse import RequestParser
from flask import g
# from app.api_0_1.common import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from app.api_0_1.common.utils import make_response, make_marshal_fields, make_response_from_pagination
from .. import api
from ..parsers.systemConfig import configFanshui
from app.models.config_fanhui import ConfigFanshui, ConfigFanshuiPc
from app.models import db
from app.models.entertainment_city import EntertainmentCity
from app.models.member import Member
from app.models.common.utils import paginate
import json
from sqlalchemy import and_, or_

'''
系统设置 - 返水设置
'''
# 返回娱乐城和对应的游戏类型
'''		AG:{"1002":0.9,"1003":0.8,"1003":0.7},
		BB:{"1002":0.4,"1003":0.3}'''


class FanAndGameType(Resource):

    def get(self):
        data = {}
        query = db.session.query(
            EntertainmentCity.code,
            EntertainmentCity.game_types).all()
        ecmap = {}
        for i in query:
            eccode = i.code
            ecmap[eccode] = {}
            gtyps = i.game_types
            if gtyps is None or gtyps == "":
                continue
            typeList = gtyps.split(",")
            for type in typeList:
                ecmap[eccode][type] = None
        data["pc_fsb"] = ecmap
        data['pc_dml'] = None
        data['pc_sx'] = None
        data['pc_jh'] = None
        # data['fanshui'] = None
        return make_response(data)


class FanAndGameSsType(Resource):

    def get(self):
        data = {}
        query = db.session.query(
            EntertainmentCity.code,
            EntertainmentCity.game_types).all()
        ecmap = {}
        for i in query:
            eccode = i.code
            ecmap[eccode] = {}
            gtyps = i.game_types

            if gtyps is None or gtyps == "":
                continue
            typeList = gtyps.split(",")
            for type in typeList:
                ecmap[eccode][type] = None
        data["fsb"] = ecmap
        return make_response(data)


fields_list = make_marshal_fields({
    'id': fields.Integer,
    'name': fields.String,
    'ss_enable': fields.Integer,
    'pc_enable': fields.Integer,
    'count': fields.Integer,

})

fields = make_marshal_fields({
    'id': fields.Integer,
    'name': fields.String,
    'fsb': fields.String,
    'pc_enable': fields.Integer,
    'ss_enable': fields.Integer,
    'count': fields.Integer,
    'agent_count': fields.Integer,
    'ss_zdlqxe': fields.Float,
    'ss_zglqxe': fields.Float,
    'ss_jh': fields.Float,
    'fendang': fields.String,
    'remark': fields.String,
    'fs_type': fields.Integer,
})


# 返水设定列表

class ConfigFanshuiListAPI(Resource):
    @marshal_with(fields_list)
    def get(self):

        list = []
        # m_result = db.session.query(ConfigFanshui).filter().all()
        m_result = db.session.query(
            ConfigFanshui.id,
            ConfigFanshui.name,
            ConfigFanshui.ss_enable,
            ConfigFanshui.pc_enable
        ).filter().all()
        if m_result:
            for i in m_result:
                count = db.session.query(Member).filter(
                    and_(Member.rebateConfig == i.id, Member.type == 0, Member.isTsetPLay != 1)).count()
                data = {}
                data['id'] = i.id
                data['name'] = i.name
                data['ss_enable'] = i.ss_enable
                data['pc_enable'] = i.pc_enable
                data['count'] = count
                list.append(data)
        return {
            'success': True,
            'data': list,
            'msg': '获取返水列表成功！'
        }


class ConfigFanshuiAPI(Resource):

    @marshal_with(fields)
    def get(self, id):
        data = {}
        count = db.session.query(Member).filter(Member.rebateConfig == id, Member.type == 0,
                                                Member.isTsetPLay != 1).count()
        agent_count = db.session.query(Member).filter(Member.defaultRebateConfig == id,
                                                      or_(Member.type == 1, Member.type == 9,
                                                          Member.type == 10)).count()
        m_result = db.session.query(ConfigFanshui).filter(ConfigFanshui.id == id)

        for i in m_result:
            data['id'] = i.id
            data['name'] = i.name
            data['ss_enable'] = i.ss_enable
            data['ss_zdlqxe'] = i.ss_zdlqxe
            data['ss_zglqxe'] = i.ss_zglqxe
            data['ss_jh'] = i.ss_jh
            data['fsb'] = i.fsb
            data['count'] = count
            data['agent_count'] = agent_count
            data['pc_enable'] = i.pc_enable
            data['remark'] = i.remark
            data['fs_type'] = i.fs_type

        m_result_pc = db.session.query(ConfigFanshuiPc).filter(ConfigFanshuiPc.fs_id == id).all()

        data['fendang'] = []
        for i in m_result_pc:
            d = {}
            d["id"] = i.id
            d["fs_id"] = i.fs_id
            d["pc_dml"] = i.pc_dml
            d["pc_sx"] = i.pc_sx
            d["pc_jh"] = i.pc_jh
            d["pc_fsb"] = json.loads(i.pc_fsb)
            data['fendang'].append(d)
        data["fendang"] = json.dumps(data['fendang'])

        return make_response(data)

    # @marshal_with(fields)
    def post(self):
        configfanshui = ConfigFanshui()
        try:
            if request.json.get('name'):
                configfanshui.name = request.json.get('name')
            if request.json.get('ss_enable'):
                configfanshui.ss_enable = request.json.get('ss_enable')
            # if request.json.get('pc_enable'):
            # 	configfanshui.pc_enable = request.json.get('pc_enable')
            if request.json.get('ss_jh'):
                configfanshui.ss_jh = request.json.get('ss_jh')
            if request.json.get('ss_zdlqxe'):
                configfanshui.ss_zdlqxe = request.json.get('ss_zdlqxe')
            if request.json.get('ss_zglqxe'):
                configfanshui.ss_zglqxe = request.json.get('ss_zglqxe')
            if request.json.get('fsb'):
                configfanshui.fsb = json.dumps(request.json.get('fsb'))
            if request.json.get('remark'):
                configfanshui.fsb = request.json.get('remark')

            db.session.add(configfanshui)
            db.session.commit()
            if request.json.get('fendang'):

                fendang = request.json.get('fendang')

                for i in fendang:
                    fanshui_pc = ConfigFanshuiPc()
                    fanshui_pc.fs_id = configfanshui.id
                    if i['pc_dml']:
                        fanshui_pc.pc_dml = i['pc_dml']
                    if i['pc_sx']:
                        fanshui_pc.pc_sx = i['pc_sx']
                    if i['pc_jh']:
                        fanshui_pc.pc_jh = i['pc_jh']
                    if i['pc_fsb']:
                        j = json.dumps(i['pc_fsb'])
                        fanshui_pc.pc_fsb = j
                    db.session.add(fanshui_pc)
                    db.session.commit()
            return {'success': True, 'message': '添加成功'}
        except:
            db.session.rollback()
            db.session.remove()
            return {'success': False, 'message': '添加失败'}

    def put(self, id):
        data = request.get_json()
        d = data['data']
        configfanshui = ConfigFanshui.query.get(id)

        try:
            if d['name']:
                configfanshui.name = d['name']
            if d['ss_enable']:
                configfanshui.ss_enable = d['ss_enable']
            if d['pc_enable']:
                configfanshui.pc_enable = d['pc_enable']
            if d['ss_jh']:
                configfanshui.ss_jh = d['ss_jh']
            if d['ss_zdlqxe']:
                configfanshui.ss_zdlqxe = d['ss_zdlqxe']
            if d['ss_zglqxe']:
                configfanshui.ss_zglqxe = d['ss_zglqxe']
            if d['fsb']:
                configfanshui.fsb = json.dumps(d['fsb'])
            if d['remark']:
                configfanshui.remark = d['remark']
            if d['fs_type']:
                configfanshui.fs_type = d['fs_type']
            # print(configfanshui.fsb)
            try:
                db.session.add(configfanshui)
                db.session.commit()

            except:
                db.session.rollback()
                db.session.remove()

            if 'delete' in d:
                num = d['delete']
                try:
                    for pc_id in num:
                        ConfigFanshuiPc.query.filter(ConfigFanshuiPc.id == pc_id).delete()
                    # db.session.delete(fanshui_pc)
                except:
                    db.session.rollback()
                    db.session.remove()

            new = d['fendang']
            # new = json.loads(new)
            for i in new:
                if 'id' in i:
                    p_id = i['id']
                    fan_pc = ConfigFanshuiPc.query.get(p_id)
                    if i['pc_dml']:
                        fan_pc.pc_dml = i['pc_dml']
                    if i['pc_sx']:
                        fan_pc.pc_sx = i['pc_sx']
                    if i['pc_jh']:
                        fan_pc.pc_jh = i['pc_jh']
                    if i['pc_fsb']:
                        fan_pc.pc_fsb = json.dumps(i['pc_fsb'])
                    try:
                        db.session.add(fan_pc)
                    except:
                        db.session.rollback()
                        db.session.remove()
                if "id" not in i:
                    try:
                        fanshui_pc = ConfigFanshuiPc()
                        fanshui_pc.fs_id = configfanshui.id
                        if i['pc_dml']:
                            fanshui_pc.pc_dml = i['pc_dml']
                        if i['pc_sx']:
                            fanshui_pc.pc_sx = i['pc_sx']
                        if i['pc_jh']:
                            fanshui_pc.pc_jh = i['pc_jh']
                        if i['pc_fsb']:
                            j = json.dumps(i['pc_fsb'])
                            fanshui_pc.pc_fsb = j

                        db.session.add(fanshui_pc)
                    except:
                        db.session.rollback()
                        db.session.remove()

            db.session.commit()
            return {'success': True, 'message': '修改成功'}
        except:
            db.session.rollback()
            db.session.remove()
            return {'success': False, 'message': '修改失败'}

    def delete(self, id):
        m_fanshui = ConfigFanshui.query.filter(ConfigFanshui.id == id).first()
        members = Member.query.filter(Member.rebateConfig == id).all()

        if m_fanshui and len(members) == 0:
            try:
                ConfigFanshui.query.filter(ConfigFanshui.id == id).delete()
                ConfigFanshuiPc.query.filter(ConfigFanshuiPc.fs_id == id).delete()

                db.session.commit()
                return {'success': True, 'message': '删除成功'}
            except:
                db.session.rollback()
                db.session.remove()
                return {'success': False, 'message': '删除失败'}
        else:
            return {'success': False, 'message': '不能删除'}


'''返水计算定时任务调试代码'''
import decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


'''返水计算'''
from app.models.blast_bets import BlastBets, BlastBetsCredit
from app.models.member_fanshui_pc import MemberFanshuiPc
from app.models.member_account_change import MemberAccountChangeRecord
from app.models.entertainment_city_bets_detail import EntertainmentCityBetsDetail
from sqlalchemy import func
from datetime import datetime, timedelta, date
import time, random
from decimal import Decimal


# 反水计算
class FanCompute(Resource):
    def get(self):
        # 1. 查询blast_bets表,获得用户uid,username,betAmount
        # 2. 查询tb_config_fanshui_pc表,获得pc_fsb,dml
        # 3. 计算反水金额amount
        now = date.today()
        yesterday = now - timedelta(days=1)
        now_time = int(time.mktime(now.timetuple()))
        yesterday_time = int(time.mktime(yesterday.timetuple()))
        # # 测试时间
        # yesterday = '2019-08-19 00:00:01'
        # now = '2019-08-19 23:59:59'
        # yesterday_time = int(time.mktime(time.strptime(yesterday, '%Y-%m-%d %H:%M:%S')))
        # now_time = int(time.mktime(time.strptime(now, '%Y-%m-%d %H:%M:%S')))

        # result_bets = db.session.query(
        #     BlastBets.uid,
        #     BlastBets.username,
        #     func.sum(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label("betAmount"),
        # ).filter(BlastBets.state == 2, BlastBets.time.between(yesterday, now)) \
        #     .group_by(BlastBets.uid, BlastBets.username).all()
        #
        # result_credit = db.session.query(
        #     BlastBetsCredit.memberId,
        #     BlastBetsCredit.memberUsername,
        #     func.sum(BlastBetsCredit.betAmount)
        # ).filter(BlastBetsCredit.state == 2, BlastBetsCredit.time.between(yesterday, now)) \
        #     .group_by(BlastBetsCredit.memberId, BlastBetsCredit.memberUsername).all()
        #
        # # 将聚合查询得到的decimal数据转为float, 再转回Python对象
        # data_bets = json.dumps(result_bets, cls=DecimalEncoder)
        # data_bets = json.loads(data_bets)
        # data_credit = json.dumps(result_credit, cls=DecimalEncoder)
        # data_credit = json.loads(data_credit)
        #
        # dict1 = {a[0]: a for a in data_bets}
        # for b in data_credit:
        #     if b[0] in dict1:
        #         dict1[b[0]][2] += b[2]
        #     else:
        #         dict1[b[0]] = b
        # data = list(dict1.values())

        # 加入娱乐城
        result_EC = db.session.query(
            EntertainmentCityBetsDetail.ECCode,
            EntertainmentCityBetsDetail.PlayerName,
            func.sum(EntertainmentCityBetsDetail.ValidBetAmount),
            EntertainmentCityBetsDetail.childType
        ).filter(EntertainmentCityBetsDetail.BetTime.between(yesterday_time, now_time)) \
            .group_by(EntertainmentCityBetsDetail.ECCode, EntertainmentCityBetsDetail.PlayerName,
                      EntertainmentCityBetsDetail.childType).all()

        actionTime = int(time.time())
        fanshuiTime = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
        for i in result_EC:
            if i[1] != None:

                reb = db.session.query(Member.rebateConfig, Member.id).filter(Member.username == i[1],
                                                                              Member.isTsetPLay != 1).first()

                if reb[0]:

                    result_fs_type = db.session.query(ConfigFanshui.fs_type, ConfigFanshui.pc_enable).filter(ConfigFanshui.id == reb[0]).first()
                    if result_fs_type[1] == 1:

                        res_fans_pc = db.session.query(ConfigFanshuiPc).filter(ConfigFanshuiPc.fs_id == reb[0]).order_by(
                            ConfigFanshuiPc.pc_dml.desc()).all()

                        pc_dml_list = []
                        for pc in res_fans_pc:
                            pc_dml_list.append(pc.pc_dml)
                            if len(pc_dml_list) == 1:
                                if i[2] >= pc.pc_dml:
                                    fsb = json.loads(pc.pc_fsb)
                                    childType = None
                                    for k, v in fsb.items():
                                        # print(k,v)
                                        if k == i[0]:
                                            for key, value in v.items():
                                                if int(key) == i[3]:
                                                    if value == None:
                                                        fsb = 0
                                                    else:
                                                        fsb = json.loads(value)
                                                    childType = int(key)
                                    # fsb = fsb['kk']['1001']
                                    # fsb = json.loads(fsb)
                                    amount = round(i[2] * fsb / 100, 2)
                                    t = int(time.time())
                                    r = random.randint(1111, 9999)
                                    fsOrderId = int(str(reb[1]) + str(t) + str(r))
                                    state = 2  # 给默认值2, 未领取


                                    member_fspc = MemberFanshuiPc()
                                    member_fspc.uid = reb[1]
                                    member_fspc.username = i[1]
                                    member_fspc.amount = amount
                                    member_fspc.betAmount = i[2]
                                    member_fspc.pc_fsb = fsb
                                    member_fspc.pc_dml = pc.pc_dml
                                    member_fspc.fsOrderId = fsOrderId
                                    member_fspc.state = state
                                    member_fspc.actionTime = actionTime
                                    # member_fspc.fanshuiTime = fanshuiTime
                                    member_fspc.fanshuiTime = '2019-08-19'
                                    member_fspc.ec_name = i[0]
                                    member_fspc.childType = childType

                                    try:
                                        db.session.add(member_fspc)
                                        db.session.commit()

                                        if result_fs_type[0] == 1:
                                            # 将返水累加到blast_members表的coin字段
                                            if member_fspc.amount:
                                                res = db.session.query(Member).filter(Member.username == i[1]).first()
                                                res.balance = res.balance + member_fspc.amount
                                                try:
                                                    db.session.add(res)
                                                    db.session.commit()

                                                    # 将tb_member_fanshui_pc表的返水状态改为state=1
                                                    member_fspc_state = db.session.query(MemberFanshuiPc).filter(
                                                        MemberFanshuiPc.id == member_fspc.id).first()
                                                    member_fspc_state.state = 1
                                                    try:
                                                        db.session.add(member_fspc_state)
                                                        db.session.commit()

                                                        # 将信息写入blast_coin_log表
                                                        coin_log = MemberAccountChangeRecord()
                                                        coin_log.memberId = member_fspc_state.uid
                                                        coin_log.amount = Decimal(str(member_fspc_state.amount))
                                                        coin_log.memberBalance = Decimal(str(res.balance))
                                                        coin_log.accountChangeType = 122
                                                        coin_log.time = int(time.time())
                                                        coin_log.info = '娱乐城%s游戏类型%s的返水' % (i[0], childType)
                                                        coin_log.auditCharge = member_fspc_state.pc_dml
                                                        coin_log.orderId = str(member_fspc_state.fsOrderId)
                                                        coin_log.rechargeid = str(member_fspc_state.fsOrderId)
                                                        coin_log.host = 0
                                                        try:
                                                            db.session.add(coin_log)
                                                            db.session.commit()
                                                        except:
                                                            db.session.rollback()
                                                            db.session.remove()
                                                    except:
                                                        db.session.rollback()
                                                        db.session.remove()

                                                except:
                                                    db.session.rollback()
                                                    db.session.remove()
                                    except:
                                        db.session.rollback()
                                        db.session.remove()

                            if len(pc_dml_list) > 1:
                                if i[2] >= pc.pc_dml and i[2] < pc_dml_list[len(pc_dml_list) - 2]:
                                    fsb = json.loads(pc.pc_fsb)

                                    childType = None
                                    for k, v in fsb.items():
                                        if k == i[0]:
                                            for key, value in v.items():
                                                if int(key) == i[3]:
                                                    if value == None:
                                                        fsb = 0
                                                    else:
                                                        fsb = json.loads(value)
                                                    childType = int(key)

                                    # fsb = fsb['kk']['1001']
                                    # fsb = json.loads(fsb)
                                    amount = round(i[2] * fsb / 100, 2)
                                    t = int(time.time())
                                    r = random.randint(1111, 9999)
                                    fsOrderId = int(str(reb[1]) + str(t) + str(r))
                                    state = 2  # 给默认值2, 未领取
                                    # actionTime = int(time.time())
                                    # fanshuiTime = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")

                                    member_fspc = MemberFanshuiPc()
                                    member_fspc.uid = reb[1]
                                    member_fspc.username = i[1]
                                    member_fspc.amount = amount
                                    member_fspc.betAmount = i[2]
                                    member_fspc.pc_fsb = fsb
                                    member_fspc.pc_dml = pc.pc_dml
                                    member_fspc.fsOrderId = fsOrderId
                                    member_fspc.state = state
                                    member_fspc.actionTime = actionTime
                                    # member_fspc.fanshuiTime = fanshuiTime
                                    member_fspc.fanshuiTime = '2019-08-19'
                                    member_fspc.ec_name = i[0]
                                    member_fspc.childType = childType
                                    try:
                                        db.session.add(member_fspc)
                                        db.session.commit()
                                        if result_fs_type[0] == 1:
                                            # 将返水累加到blast_members表的coin字段
                                            if member_fspc.amount:
                                                res = db.session.query(Member).filter(Member.username == i[1]).first()
                                                res.balance = res.balance + member_fspc.amount
                                                try:
                                                    db.session.add(res)
                                                    db.session.commit()

                                                    # 将tb_member_fanshui_pc表的返水状态改为state=1
                                                    member_fspc_state = db.session.query(MemberFanshuiPc).filter(
                                                        MemberFanshuiPc.id == member_fspc.id).first()
                                                    member_fspc_state.state = 1

                                                    try:
                                                        db.session.add(member_fspc_state)
                                                        db.session.commit()

                                                        # 将信息写入blast_coin_log表
                                                        coin_log = MemberAccountChangeRecord()
                                                        coin_log.memberId = member_fspc_state.uid
                                                        coin_log.amount = member_fspc_state.amount
                                                        coin_log.memberBalance = res.balance
                                                        coin_log.accountChangeType = 122
                                                        coin_log.time = int(time.time())
                                                        coin_log.info = '娱乐城%s游戏类型%s的返水' % (i[0], childType)
                                                        coin_log.auditCharge = member_fspc_state.pc_dml
                                                        coin_log.orderId = str(member_fspc_state.fsOrderId)
                                                        coin_log.rechargeid = str(member_fspc_state.fsOrderId)
                                                        coin_log.host = 0

                                                        try:
                                                            db.session.add(coin_log)
                                                            db.session.commit()

                                                        except:
                                                            db.session.rollback()
                                                            db.session.remove()
                                                    except:
                                                        db.session.rollback()
                                                        db.session.remove()

                                                except:
                                                    db.session.rollback()
                                                    db.session.remove()
                                    except:
                                        db.session.rollback()
                                        db.session.remove()

        # # 根据uid去查blast_members表,查出相应的pc_fsb, dml
        # # uid : i[0]
        # for i in data:
        #     reb = db.session.query(Member.rebateConfig).filter(Member.id == i[0], Member.isTsetPLay != 1).first()
        #
        #     if reb:
        #         result_fs_type = db.session.query(ConfigFanshui.fs_type).filter(ConfigFanshui.id == reb[0]).first()
        #
        #         res_fans_pc = db.session.query(ConfigFanshuiPc).filter(ConfigFanshuiPc.fs_id == reb[0]).order_by(
        #             ConfigFanshuiPc.pc_dml.desc()).all()
        #
        #         pc_dml_list = []
        #         for pc in res_fans_pc:
        #             pc_dml_list.append(pc.pc_dml)
        #             if len(pc_dml_list) == 1:
        #                 if i[2] >= pc.pc_dml:
        #
        #                     fsb = json.loads(pc.pc_fsb)
        #                     fsb = fsb['kk']['1001']
        #                     if fsb == None:
        #                         fsb = 0
        #                     else:
        #                         fsb = json.loads(fsb)
        #                     amount = round(i[2] * fsb / 100, 2)
        #                     t = int(time.time())
        #                     r = random.randint(1111, 9999)
        #                     fsOrderId = int(str(i[0]) + str(t) + str(r))
        #                     state = 2  # 给默认值2, 未领取
        #                     actionTime = int(time.time())
        #                     fanshuiTime = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
        #
        #                     member_fspc = MemberFanshuiPc()
        #                     member_fspc.uid = i[0]
        #                     member_fspc.username = i[1]
        #                     member_fspc.amount = amount
        #                     member_fspc.betAmount = i[2]
        #                     member_fspc.pc_fsb = fsb
        #                     member_fspc.pc_dml = pc.pc_dml
        #                     member_fspc.fsOrderId = fsOrderId
        #                     member_fspc.state = state
        #                     member_fspc.actionTime = actionTime
        #                     # member_fspc.fanshuiTime = fanshuiTime
        #                     member_fspc.fanshuiTime = '2019-08-03'
        #                     member_fspc.ec_name = 'KK'
        #                     member_fspc.childType = 1001
        #
        #                     try:
        #                         db.session.add(member_fspc)
        #                         db.session.commit()
        #                         if result_fs_type[0] == 1:
        #                             # 将返水累加到blast_members表的coin字段
        #                             if member_fspc.amount:
        #                                 res = db.session.query(Member).filter(Member.id == i[0]).first()
        #                                 res.balance = res.balance + member_fspc.amount
        #                                 try:
        #                                     db.session.add(res)
        #                                     db.session.commit()
        #
        #                                     # 将tb_member_fanshui_pc表的返水状态改为state=1
        #                                     member_fspc_state = db.session.query(MemberFanshuiPc).filter(
        #                                         MemberFanshuiPc.id == member_fspc.id).first()
        #                                     member_fspc_state.state = 1
        #                                     try:
        #                                         db.session.add(member_fspc_state)
        #                                         db.session.commit()
        #
        #                                         # 将信息写入blast_coin_log表
        #                                         coin_log = MemberAccountChangeRecord()
        #                                         coin_log.memberId = member_fspc_state.uid
        #                                         coin_log.amount = member_fspc_state.amount
        #                                         coin_log.memberBalance = res.balance
        #                                         coin_log.accountChangeType = 122
        #                                         coin_log.time = int(time.time())
        #                                         coin_log.info = 'KK返水'
        #                                         coin_log.auditCharge = member_fspc_state.pc_dml
        #                                         coin_log.rechargeid = str(member_fspc_state.fsOrderId)
        #                                         coin_log.host = 0
        #                                         try:
        #                                             db.session.add(coin_log)
        #                                             db.session.commit()
        #                                         except:
        #                                             db.session.rollback()
        #                                             db.session.remove()
        #                                     except:
        #                                         db.session.rollback()
        #                                         db.session.remove()
        #
        #                                 except:
        #                                     db.session.rollback()
        #                                     db.session.remove()
        #                     except:
        #                         db.session.rollback()
        #                         db.session.remove()
        #
        #             if len(pc_dml_list) > 1:
        #                 if i[2] >= pc.pc_dml and i[2] < pc_dml_list[len(pc_dml_list) - 2]:
        #                     fsb = json.loads(pc.pc_fsb)
        #                     fsb = fsb['kk']['1001']
        #                     if fsb == None:
        #                         fsb = 0
        #                     else:
        #                         fsb = json.loads(fsb)
        #                     amount = round(i[2] * fsb / 100, 2)
        #                     t = int(time.time())
        #                     r = random.randint(1111, 9999)
        #                     fsOrderId = int(str(i[0]) + str(t) + str(r))
        #                     state = 2  # 给默认值2, 未领取
        #                     actionTime = int(time.time())
        #                     fanshuiTime = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
        #
        #                     member_fspc = MemberFanshuiPc()
        #                     member_fspc.uid = i[0]
        #                     member_fspc.username = i[1]
        #                     member_fspc.amount = amount
        #                     member_fspc.betAmount = i[2]
        #                     member_fspc.pc_fsb = fsb
        #                     member_fspc.pc_dml = pc.pc_dml
        #                     member_fspc.fsOrderId = fsOrderId
        #                     member_fspc.state = state
        #                     member_fspc.actionTime = actionTime
        #                     # member_fspc.fanshuiTime = fanshuiTime
        #                     member_fspc.fanshuiTime = '2019-08-03'
        #                     member_fspc.ec_name = 'KK'
        #                     member_fspc.childType = 1001
        #
        #                     try:
        #                         db.session.add(member_fspc)
        #                         db.session.commit()
        #
        #                         if result_fs_type[0] == 1:
        #                             # 将返水累加到blast_members表的coin字段
        #                             if member_fspc.amount:
        #                                 res = db.session.query(Member).filter(Member.id == i[0]).first()
        #                                 res.balance = res.balance + member_fspc.amount
        #                                 try:
        #                                     db.session.add(res)
        #                                     db.session.commit()
        #
        #                                     # 将tb_member_fanshui_pc表的返水状态改为state=1
        #                                     member_fspc_state = db.session.query(MemberFanshuiPc).filter(
        #                                         MemberFanshuiPc.id == member_fspc.id).first()
        #                                     member_fspc_state.state = 1
        #                                     try:
        #                                         db.session.add(member_fspc_state)
        #                                         db.session.commit()
        #
        #                                         # 将信息写入blast_coin_log表
        #                                         coin_log = MemberAccountChangeRecord()
        #                                         coin_log.memberId = member_fspc_state.uid
        #                                         coin_log.amount = member_fspc_state.amount
        #                                         coin_log.memberBalance = res.balance
        #                                         coin_log.accountChangeType = 122
        #                                         coin_log.time = int(time.time())
        #                                         coin_log.info = 'KK返水'
        #                                         coin_log.auditCharge = member_fspc_state.pc_dml
        #                                         coin_log.orderId = str(member_fspc_state.fsOrderId)
        #                                         coin_log.rechargeid = str(member_fspc_state.fsOrderId)
        #                                         coin_log.host = 0
        #
        #                                         try:
        #                                             db.session.add(coin_log)
        #                                             db.session.commit()
        #                                         except:
        #                                             db.session.rollback()
        #                                             db.session.remove()
        #                                     except:
        #                                         db.session.rollback()
        #                                         db.session.remove()
        #
        #                                 except:
        #                                     db.session.rollback()
        #                                     db.session.remove()
        #                     except:
        #                         db.session.rollback()
        #                         db.session.remove()

        # return 'True'
        pass

# 会员手动领取返水接口
class GetFanshui(Resource):
    def get(self):
        # 将返水累加到blast_members表的coin字段
        if not hasattr(g, 'current_member'):
            return {
                'errorCode': "9999",
                'errorMsg': "用戶未登录",
                'success': False
            }
        uid = g.current_member.id
        res_fanshui = db.session.query(MemberFanshuiPc.uid, func.sum(MemberFanshuiPc.amount)).filter(MemberFanshuiPc.uid == uid, MemberFanshuiPc.state==2).first()

        if res_fanshui:
            res = db.session.query(Member).filter(Member.id == uid).first()
            res.balance = res.balance + round(res_fanshui[1], 2)

            try:
                db.session.add(res)
                db.session.commit()

                # 将tb_member_fanshui_pc表的返水状态改为state=1
                member_fspc_state = db.session.query(MemberFanshuiPc).filter(
                    MemberFanshuiPc.uid == res_fanshui[0]).all()

                for i in member_fspc_state:
                    i.state = 1
                    try:
                        db.session.add(i)
                        db.session.commit()

                        # 将信息写入blast_coin_log表
                        coin_log = MemberAccountChangeRecord()
                        coin_log.memberId = member_fspc_state.uid
                        coin_log.amount = Decimal(str(member_fspc_state.amount))
                        coin_log.memberBalance = Decimal(str(res.balance))
                        coin_log.accountChangeType = 122
                        coin_log.time = int(time.time())
                        coin_log.info = '用户%s手动领取的批次返水' % (res_fanshui[0])
                        coin_log.auditCharge = member_fspc_state.pc_dml
                        coin_log.orderId = str(member_fspc_state.fsOrderId)
                        coin_log.rechargeid = str(member_fspc_state.fsOrderId)
                        coin_log.host = 0
                        try:
                            db.session.add(coin_log)
                            db.session.commit()
                        except:
                            db.session.rollback()
                            db.session.remove()
                    except:
                        db.session.rollback()
                        db.session.remove()

            except:
                db.session.rollback()
                db.session.remove()
            return {"success": True}
        else:
            return {"success": False}




# 动态设置定时器执行的时间
from app.schedule.fanshui_compute import fs_job
from app.schedule import scheduler
from flask import current_app
class ApschedTime(Resource):
    def get(self):
        parser = RequestParser(trim=True)
        parser.add_argument('hour', type=int)
        parser.add_argument('minute', type=int)
        args = parser.parse_args(strict=True)

        hour = int(request.args.get('hour'))
        minute = int(request.args.get('minute'))

        now = date.today()
        yesterday = now - timedelta(days=1)
        nextday = now + timedelta(days=1)

        yes_day = yesterday.strftime('%Y-%m-%d')
        res_time = db.session.query(MemberFanshuiPc.fanshuiTime).filter().order_by(MemberFanshuiPc.id.desc()).first()

        if yes_day == res_time[0]:
            job = {
                    'id': 'FanshuiJob',  # 任务的唯一ID，不要冲突
                    'func': 'fs_job',  # 执行任务的function名称
                    'args': '',  # 如果function需要参数，就在这里添加
                }
            scheduler.remove_job('FanshuiJob')
            current_app.apscheduler.add_job(func=__name__+':'+job['func'], id=job['id'], trigger='cron', hour=hour, minute=minute, start_date=nextday)
        else:
            job = {
                'id': 'FanshuiJob',
                'func': 'fs_job',
                'args': '',
            }
            scheduler.remove_job('FanshuiJob')
            current_app.apscheduler.add_job(func=__name__+':'+job['func'], id=job['id'], trigger='cron', hour=hour, minute=minute)

        return {"success": True}

        # h = datetime.now().hour
        # m = datetime.now().minute
        #
        # if hour < h or (hour==h and minute<m):
        #
        #     job = {
        #         'id': 'FanshuiJob',  # 任务的唯一ID，不要冲突
        #         'func': 'fs_job',  # 执行任务的function名称
        #         'args': '',  # 如果function需要参数，就在这里添加
        #     }
        #     scheduler.remove_job('FanshuiJob')
        #     current_app.apscheduler.add_job(func=__name__+':'+job['func'], id=job['id'], trigger='cron', hour=hour, minute=minute)
        #
        #     return {"success": True}
        # else:
        #     return {"success": False, 'errorMsg': '您修改的时间不正确'}

