from app.models import db
from app.models.member import Member
from app.models.config_fanhui import ConfigFanshuiPc, ConfigFanshui
import decimal, json
from app.schedule import scheduler


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

def fs_job():
    # 1. 查询blast_bets表,获得用户uid,username,betAmount
    # 2. 查询tb_config_fanshui_pc表,获得pc_fsb,dml
    # 3. 计算反水金额amount
    with scheduler.app.app_context():
        now = date.today()
        yesterday = now - timedelta(days=1)
        now_time = int(time.mktime(now.timetuple()))
        yesterday_time = int(time.mktime(yesterday.timetuple()))

        # # 测试时间
        # yesterday = '2019-08-13 00:00:01'
        # now = '2019-08-13 23:59:59'
        # yesterday_time = int(time.mktime(time.strptime(yesterday, '%Y-%m-%d %H:%M:%S')))
        # now_time = int(time.mktime(time.strptime(now, '%Y-%m-%d %H:%M:%S')))

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
                    result_fs_type = db.session.query(ConfigFanshui.fs_type, ConfigFanshui.pc_enable).filter(
                        ConfigFanshui.id == reb[0]).first()
                    if result_fs_type[1] == 1:
                        res_fans_pc = db.session.query(ConfigFanshuiPc).filter(
                            ConfigFanshuiPc.fs_id == reb[0]).order_by(
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
                                    member_fspc.fanshuiTime = fanshuiTime
                                    # member_fspc.fanshuiTime = '2019-08-19'
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
                                    member_fspc.fanshuiTime = fanshuiTime
                                    # member_fspc.fanshuiTime = '2019-08-19'
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
        # now = date.today()
        # yesterday = now - timedelta(days=1)
        # now_time = int(time.mktime(now.timetuple()))
        # yesterday_time = int(time.mktime(yesterday.timetuple()))
        #
        # # 测试时间
        # # yesterday = '2019-08-10 00:00:01'
        # # now = '2019-08-10 23:59:59'
        # # yesterday_time = int(time.mktime(time.strptime(yesterday, '%Y-%m-%d %H:%M:%S')))
        # # now_time = int(time.mktime(time.strptime(now, '%Y-%m-%d %H:%M:%S')))
        #
        # # 加入娱乐城
        # result_EC = db.session.query(
        #     EntertainmentCityBetsDetail.ECCode,
        #     EntertainmentCityBetsDetail.PlayerName,
        #     func.sum(EntertainmentCityBetsDetail.ValidBetAmount),
        #     EntertainmentCityBetsDetail.childType
        # ).filter(EntertainmentCityBetsDetail.BetTime.between(yesterday_time, now_time)) \
        #     .group_by(EntertainmentCityBetsDetail.ECCode, EntertainmentCityBetsDetail.PlayerName,
        #               EntertainmentCityBetsDetail.childType).all()
        #
        # for i in result_EC:
        #     if i[1] != None:
        #         reb = db.session.query(Member.rebateConfig, Member.id).filter(Member.username == i[1],
        #                                                                       Member.isTsetPLay != 1).first()
        #
        #         if reb[0]:
        #             result_fs_type = db.session.query(ConfigFanshui.fs_type).filter(ConfigFanshui.id == reb[0]).first()
        #
        #             res_fans_pc = db.session.query(ConfigFanshuiPc).filter(ConfigFanshuiPc.fs_id == reb[0]).order_by(
        #                 ConfigFanshuiPc.pc_dml.desc()).all()
        #
        #             pc_dml_list = []
        #             for pc in res_fans_pc:
        #                 pc_dml_list.append(pc.pc_dml)
        #                 if len(pc_dml_list) == 1:
        #                     if i[2] >= pc.pc_dml:
        #                         fsb = json.loads(pc.pc_fsb)
        #                         childType = None
        #                         for k, v in fsb.items():
        #                             # print(k,v)
        #                             if k == i[0]:
        #                                 for key, value in v.items():
        #                                     if int(key) == i[3]:
        #                                         if value == None:
        #                                             fsb = 0
        #                                         else:
        #                                             fsb = json.loads(value)
        #                                         childType = int(key)
        #                         # fsb = fsb['kk']['1001']
        #                         # fsb = json.loads(fsb)
        #                         amount = round(i[2] * fsb / 100, 2)
        #                         t = int(time.time())
        #                         r = random.randint(1111, 9999)
        #                         fsOrderId = int(str(reb[1]) + str(t) + str(r))
        #                         state = 2  # 给默认值2, 未领取
        #                         actionTime = int(time.time())
        #                         fanshuiTime = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
        #
        #                         member_fspc = MemberFanshuiPc()
        #                         member_fspc.uid = reb[1]
        #                         member_fspc.username = i[1]
        #                         member_fspc.amount = amount
        #                         member_fspc.betAmount = i[2]
        #                         member_fspc.pc_fsb = fsb
        #                         member_fspc.pc_dml = pc.pc_dml
        #                         member_fspc.fsOrderId = fsOrderId
        #                         member_fspc.state = state
        #                         member_fspc.actionTime = actionTime
        #                         member_fspc.fanshuiTime = fanshuiTime
        #                         # member_fspc.fanshuiTime = '2019-08-10'
        #                         member_fspc.ec_name = i[0]
        #                         member_fspc.childType = childType
        #
        #                         try:
        #                             db.session.add(member_fspc)
        #                             db.session.commit()
        #
        #                             if result_fs_type[0] == 1:
        #                                 # 将返水累加到blast_members表的coin字段
        #                                 if member_fspc.amount:
        #                                     res = db.session.query(Member).filter(Member.username == i[1]).first()
        #                                     res.balance = res.balance + member_fspc.amount
        #                                     try:
        #                                         db.session.add(res)
        #                                         db.session.commit()
        #
        #                                         # 将tb_member_fanshui_pc表的返水状态改为state=1
        #                                         member_fspc_state = db.session.query(MemberFanshuiPc).filter(
        #                                             MemberFanshuiPc.id == member_fspc.id).first()
        #                                         member_fspc_state.state = 1
        #                                         try:
        #                                             db.session.add(member_fspc_state)
        #                                             db.session.commit()
        #
        #                                             # 将信息写入blast_coin_log表
        #                                             coin_log = MemberAccountChangeRecord()
        #                                             coin_log.memberId = member_fspc_state.uid
        #                                             coin_log.amount = Decimal(str(member_fspc_state.amount))
        #                                             coin_log.memberBalance = Decimal(str(res.balance))
        #                                             coin_log.accountChangeType = 122
        #                                             coin_log.time = int(time.time())
        #                                             coin_log.info = '娱乐城%s游戏类型%s的返水' % (i[0], childType)
        #                                             coin_log.auditCharge = member_fspc_state.pc_dml
        #                                             coin_log.orderId = str(member_fspc_state.fsOrderId)
        #                                             coin_log.rechargeid = str(member_fspc_state.fsOrderId)
        #                                             coin_log.host = 0
        #                                             try:
        #                                                 db.session.add(coin_log)
        #                                                 db.session.commit()
        #                                             except:
        #                                                 db.session.rollback()
        #                                                 db.session.remove()
        #                                         except:
        #                                             db.session.rollback()
        #                                             db.session.remove()
        #
        #                                     except:
        #                                         db.session.rollback()
        #                                         db.session.remove()
        #                         except:
        #                             db.session.rollback()
        #                             db.session.remove()
        #
        #                 if len(pc_dml_list) > 1:
        #                     if i[2] >= pc.pc_dml and i[2] < pc_dml_list[len(pc_dml_list) - 2]:
        #                         fsb = json.loads(pc.pc_fsb)
        #
        #                         childType = None
        #                         for k, v in fsb.items():
        #                             # print(k,v)
        #                             if k == i[0]:
        #                                 for key, value in v.items():
        #                                     if int(key) == i[3]:
        #                                         if value == None:
        #                                             fsb = 0
        #                                         else:
        #                                             fsb = json.loads(value)
        #                                         childType = int(key)
        #
        #                         # fsb = fsb['kk']['1001']
        #                         # fsb = json.loads(fsb)
        #                         amount = round(i[2] * fsb / 100, 2)
        #                         t = int(time.time())
        #                         r = random.randint(1111, 9999)
        #                         fsOrderId = int(str(reb[1]) + str(t) + str(r))
        #                         state = 2  # 给默认值2, 未领取
        #                         actionTime = int(time.time())
        #                         fanshuiTime = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
        #
        #                         member_fspc = MemberFanshuiPc()
        #                         member_fspc.uid = reb[1]
        #                         member_fspc.username = i[1]
        #                         member_fspc.amount = amount
        #                         member_fspc.betAmount = i[2]
        #                         member_fspc.pc_fsb = fsb
        #                         member_fspc.pc_dml = pc.pc_dml
        #                         member_fspc.fsOrderId = fsOrderId
        #                         member_fspc.state = state
        #                         member_fspc.actionTime = actionTime
        #                         member_fspc.fanshuiTime = fanshuiTime
        #                         # member_fspc.fanshuiTime = '2019-08-10'
        #                         member_fspc.ec_name = i[0]
        #                         member_fspc.childType = childType
        #                         try:
        #                             db.session.add(member_fspc)
        #                             db.session.commit()
        #                             if result_fs_type[0] == 1:
        #                                 # 将返水累加到blast_members表的coin字段
        #                                 if member_fspc.amount:
        #                                     res = db.session.query(Member).filter(Member.username == i[1]).first()
        #                                     res.balance = res.balance + member_fspc.amount
        #                                     try:
        #                                         db.session.add(res)
        #                                         db.session.commit()
        #
        #                                         # 将tb_member_fanshui_pc表的返水状态改为state=1
        #                                         member_fspc_state = db.session.query(MemberFanshuiPc).filter(
        #                                             MemberFanshuiPc.id == member_fspc.id).first()
        #                                         member_fspc_state.state = 1
        #
        #                                         try:
        #                                             db.session.add(member_fspc_state)
        #                                             db.session.commit()
        #
        #                                             # 将信息写入blast_coin_log表
        #                                             coin_log = MemberAccountChangeRecord()
        #                                             coin_log.memberId = member_fspc_state.uid
        #                                             coin_log.amount = member_fspc_state.amount
        #                                             coin_log.memberBalance = res.balance
        #                                             coin_log.accountChangeType = 122
        #                                             coin_log.time = int(time.time())
        #                                             coin_log.info = '娱乐城%s游戏类型%s的返水' % (i[0], childType)
        #                                             coin_log.auditCharge = member_fspc_state.pc_dml
        #                                             coin_log.orderId = str(member_fspc_state.fsOrderId)
        #                                             coin_log.rechargeid = str(member_fspc_state.fsOrderId)
        #                                             coin_log.host = 0
        #
        #                                             try:
        #                                                 db.session.add(coin_log)
        #                                                 db.session.commit()
        #
        #                                             except:
        #                                                 db.session.rollback()
        #                                                 db.session.remove()
        #                                         except:
        #                                             db.session.rollback()
        #                                             db.session.remove()
        #
        #                                     except:
        #                                         db.session.rollback()
        #                                         db.session.remove()
        #                         except:
        #                             db.session.rollback()
        #                             db.session.remove()
