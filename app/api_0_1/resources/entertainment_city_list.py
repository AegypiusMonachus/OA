import random

from flask import g, jsonify, request, current_app
from flask_apscheduler import json
from sqlalchemy import and_, distinct, func
import time
from app.api_0_1.common import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from app.common.orderUtils import createOrderIdNew
from app.common.utils import time_to_value, host_to_value
from app.entertainmentcity import EntertainmentCityFactory
from app.entertainmentcity.amountTransfer import AmountTransfer
from app.models import db
from app.models.common.utils import paginate
from app.models.entertainment_city import EntertainmentCity, EntertainmentCity_get_qb
from app.models.entertainment_city_list import OperationalRecord

from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser

from app.models.entertainment_city_log import EntertainmentCityTradeLog,EntertainmentCityTradeDetail
from app.models.member import Member
from app.models.member_account_change import Deposit, MemberAccountChangeRecord
from app.models.memeber_history import OperationHistory
from app.models.user import User
from ..common.utils import *
from sqlalchemy import or_

# 获取娱乐城信息
class GetEntertainmentCityList(Resource):

    def get(self):
        parser = RequestParser(trim=True)
        parser.add_argument('name', type=str)
        args = parser.parse_args(strict=True)
        if 'name' in args and args["name"] is not None:
            city_args = db.session.query(EntertainmentCity).filter(EntertainmentCity.code == args['name']).all()
            result = []
            data = {}
            for args in city_args:
                data['id'] = args.id
                data['name'] = args.code
                data['enable'] = args.enable
                count = db.session.query(EntertainmentCityTradeLog).filter(EntertainmentCityTradeLog.state == 2,or_(EntertainmentCityTradeLog.ec == args.name,EntertainmentCityTradeLog.last_ec == args.name)).count()
                coin = db.session.query(func.sum(EntertainmentCityTradeLog.amount)).filter(EntertainmentCityTradeLog.state == 2,or_(
                    EntertainmentCityTradeLog.ec == args.name,
                    EntertainmentCityTradeLog.last_ec == args.name)).scalar()
                data['FillTransferCount'] = count
                data['FillTransferSum'] = coin
                result.append(data)
            return make_response(result)

        else:
            city_args = db.session.query(EntertainmentCity).filter(EntertainmentCity.code != 'kk').all()
            result = []

            for args in city_args:
                data = {}
                data['id'] = args.id
                data['name'] = args.code
                data['enable'] = args.enable
                count = db.session.query(EntertainmentCityTradeLog).filter(EntertainmentCityTradeLog.state == 2, or_(
                    EntertainmentCityTradeLog.ec == args.name,
                    EntertainmentCityTradeLog.last_ec == args.name)).count()
                coin = db.session.query(func.sum(EntertainmentCityTradeLog.amount)).filter(EntertainmentCityTradeLog.state == 2,or_(
                    EntertainmentCityTradeLog.ec == args.name,
                    EntertainmentCityTradeLog.last_ec == args.name)).scalar()
                data['FillTransferCount'] = count
                data['FillTransferSum'] = coin
                result.append(data)
            return make_response(result)


     # 修改娱乐城状态
    def put(self):
        parser = RequestParser(trim=True)
        parser.add_argument('enable', type=int)
        parser.add_argument('name', type=str)
        args = parser.parse_args()
        args = {key: value for key, value in args.items() if value is not None}
        if args['enable'] == 1:
            try:
                EntertainmentCity.query.filter(EntertainmentCity.code == args['name']).update(args)
                history = OperationalRecord()
                history.username = g.current_user.username
                history.creatTime = time_to_value()
                history.remark = "开启%s"%args['name']
                history.ylc = args['name']
                db.session.add(history)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.remove()
        else:
            try:
                EntertainmentCity.query.filter(EntertainmentCity.code == args['name']).update(args)
                history = OperationalRecord()
                history.username = g.current_user.username
                history.creatTime = time_to_value()
                history.remark = "关闭%s"%args['name']
                history.ylc = args['name']
                db.session.add(history)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.remove()
        return {'success':True}



# 检视历史记录模糊查询
class SearchRecord(Resource):
    def get(self):
        parser = RequestParser()
        parser.add_argument('page', type=int, default=DEFAULT_PAGE)
        parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

        parser.add_argument('name', type=str)
        parser.add_argument('starttime', type=int)
        parser.add_argument('endtime', type=int)
        parser.add_argument('include', type=str)
        parser.add_argument('exclude', type=str)
        parser.add_argument('username', type=str)
        args = parser.parse_args(strict=True)

        criterion = set()
        criterion.add(OperationalRecord.ylc == args['name'])
        if args['starttime']:
            criterion.add(OperationalRecord.creatTime >= args['starttime'])
        if args['endtime']:
            criterion.add(OperationalRecord.creatTime <= args['endtime'])
        if args["include"]:
            a = args["include"].split(',')
            b = []
            for i in a:
                c = '%{}%'.format(i)
                b.append(c)
            criterion.add(or_(*[OperationalRecord.remark.like(w) for w in b]))
        if args["exclude"]:
            a = args["exclude"].split(',')
            b = []
            for i in a:
                c = '%{}%'.format(i)
                b.append(c)
            criterion.add(and_(*[OperationalRecord.remark.notlike(w) for w  in b]))
        if args['username']:
            criterion.add(OperationalRecord.username == args['username'])

        query = db.session.query(OperationalRecord).order_by(OperationalRecord.creatTime.desc())
        result = []
        pagination = paginate(query, criterion, args['page'], args['pageSize'])
        for item in pagination.items:
            result.append({
                'id': item.id,
                'username': item.username,
                'createtime': item.creatTime,
                'remark': item.remark
            })
        return make_response(result, page=pagination.page, pages=pagination.pages, total=pagination.total)


# 取回所有钱包接口
class GetallWalletevery(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('toEC', type=str, required=True)
        parser.add_argument('fromEC', type=str, required=True)
        kargs = parser.parse_args()

        shijianchuo = int(time.time())
        actiontime = shijianchuo - 2592000
        users = db.session.query(distinct(EntertainmentCityTradeLog.username),EntertainmentCityTradeLog.uid).filter(
            EntertainmentCityTradeLog.ec == kargs['fromEC'], EntertainmentCityTradeLog.state == 1,EntertainmentCityTradeLog.actionTime > actiontime).all()
        if not users:
            return {"errorMsg":"目前没有会员创建该娱乐城钱包"}
        r_data = {}
        for user in users:
            name = list(user)
            t_name = name[0]

            mContext = {}
            duixiang = Member.query.filter(Member.username == t_name).first()
            mContext["member"] = duixiang
            mContext['loginEC'] = kargs['toEC']
            mContext["ip"] = host_to_value(request.remote_addr)
            mContext["real_ip"] = request.remote_addr
            current_app.logger.info(
                '---------%s从%s取回会员钱包到主账户开始------------' % (g.current_user.username, kargs['fromEC']))
            r_data = AmountTransfer.withdrawalToAccount(mContext, kargs)
            current_app.logger.info(
                '---------%s从%s取回会员钱包到主账户结束------------' % (g.current_user.username, kargs['fromEC']))

        history = OperationalRecord()
        history.username = g.current_user.username
        history.creatTime = time_to_value()
        history.remark = "取回%s所有钱包" % kargs['fromEC']
        history.ylc = kargs['fromEC']
        try:
            db.session.add(history)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()

        return r_data


# 更新所有钱包
class UpdataallWallet:

    def __init__(self, name):
        self.username = name

    def everybalence(self, code,name):
        member = UpdataallWallet(name)
        ce = EntertainmentCityFactory.getEntertainmentCity(code)
        ce.context["member"] = member.username
        m_data = ce.updatebalance(ce.context["member"])
        return m_data

# 更新所有钱包接口
class UpdataallWalletEvery(Resource):

    def post(self):
        parser = RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('pageSize', type=int)

        parser.add_argument('code', type=str)
        args = parser.parse_args()
        shijianchuo = int(time.time())
        actiontime =  shijianchuo - 2592000

        criterion = set()
        criterion.add(EntertainmentCityTradeLog.ec ==args['code'])
        criterion.add(EntertainmentCityTradeLog.state == 1)
        criterion.add(EntertainmentCityTradeLog.actionTime > actiontime)

        query = db.session.query(distinct(EntertainmentCityTradeLog.username))
        pagination = paginate(query, criterion, args['page'], args['pageSize'])

        if not pagination.items:
            return {"errorMsg":"目前没有会员创建该娱乐城钱包"}

        result = []
        for user in pagination.items:
            data = {}
            user = list(user)
            user = (' '.join(user))
            data['username'] = user
            data['code'] = args['code']
            member = UpdataallWallet(user)
            m_data = member.everybalence(args['code'],user)
            m_data = m_data.content.decode()
            m_data = json.loads(m_data)
           # '''{"Guid": "cf2bce64-528b-40dd-8d1a-a9afae96ee5b", "Success": true, "Code": "0", "Message": "Success", "Data": {"balance": "0", "CurrencyCode": null}}'''
            if m_data['Code'] == "0":
                data['state'] = 1
                data['balance'] = "%.2f" % float(m_data['Data']['balance'])
                result.append(data)
            else:
                data['state'] = 0
                data['balance'] = '--'
                result.append(data)
        history = OperationalRecord()
        history.username = g.current_user.username
        history.creatTime = time_to_value()
        history.remark = "更新%s所有钱包" % args['code']
        history.ylc = args['code']
        try:
            db.session.add(history)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
        return make_response(result, page=pagination.page, pages=pagination.pages, total=pagination.total)



'''娱乐城转账用户名模糊搜索'''
class Uname(Resource):

    def get(self):
        parser = RequestParser()
        parser.add_argument('username')
        args = parser.parse_args()
        # 发件人
        if args["username"]:
            username = args["username"]
            query = db.session.query(distinct(EntertainmentCityTradeLog.username)).filter(EntertainmentCityTradeLog.username.like("%{}%".format(username))).all()
            result = []
            for name in query:
                data={}
                truename = list(name)
                truename = (' '.join(truename))
                data['name'] = truename
                result.append(data)
            return 	make_response(result)


'''获取娱乐城名称'''
class GetYlcName(Resource):

    def get(self):
        query = db.session.query(
            EntertainmentCity.code,
           ).all()
        result = []
        for i in query:
            data = {}
            a = (' '.join(i))
            data['GameName'] = a
            result.append(data)
        result1 = []
        for i in result:
            if i['GameName'] != "kk":
                result1.append(i)


        return make_response(result1)


"""娱乐城转账记录查询"""
class TransferLog(Resource):

    def get(self):
        parser = RequestParser(trim=True)
        parser.add_argument('page', type=int, default=DEFAULT_PAGE)
        parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

        parser.add_argument('username', type=str)
        parser.add_argument('yulecheng', type=str)
        parser.add_argument('TimeLower', type=int)
        parser.add_argument('TimeUpper', type=int)
        args = parser.parse_args(strict=True)

        criterion = set()
        if 'username' in args and args['username'] is not None:
            criterion.add(EntertainmentCityTradeLog.username == args['username'])
        else:
            return {"errorMsg": "账号不能为空"}
        if 'yulecheng' in args and args['yulecheng'] is not None:
            ylcname = args['yulecheng'].split(',')
            if ylcname is not None:

                criterion.add(or_(EntertainmentCityTradeLog.ec.in_(ylcname),EntertainmentCityTradeLog.last_ec.in_(ylcname)))
        else:
            return {"errorMsg": "请选择要查询的娱乐城"}
        if 'TimeLower' in args and args['TimeLower'] is not None:
            criterion.add(EntertainmentCityTradeLog.actionTime >= args['TimeLower'])
        else:
            return {"errorMsg": "请填写起始时间"}
        if 'TimeUpper' in args and args['TimeUpper'] is not None:
            criterion.add(EntertainmentCityTradeLog.actionTime <= args['TimeUpper'])
        else:
            return {"errorMsg": "请填写结束时间"}
        query = db.session.query(
            EntertainmentCityTradeLog.id,
            EntertainmentCityTradeLog.uid,
            EntertainmentCityTradeLog.username,
            EntertainmentCityTradeLog.ec,
            EntertainmentCityTradeLog.last_ec,
            EntertainmentCityTradeLog.actionTime,
            EntertainmentCityTradeLog.orderid,
            EntertainmentCityTradeLog.amount,
            EntertainmentCityTradeLog.state,
            EntertainmentCityTradeLog.type
             ).order_by(EntertainmentCityTradeLog.actionTime.desc())
        result = []
        pagination = paginate(query, criterion, args['page'], args['pageSize'])
        for item in pagination.items:
            result.append({
                'id':item.id,
                'uid':item.uid,
                'username' :item.username,
                'ec' :item.ec,
                'last_ec' : item.last_ec,
                'actionTime' :item.actionTime,
                'orderid' : item.orderid,
                'amount' : item.amount,
                'state':item.state,
                'type':item.type
            })
        return make_response(result, page=pagination.page, pages=pagination.pages, total=pagination.total)



class TransferSure(Resource):

    def get(self):
        parser = RequestParser(trim=True)
        parser.add_argument('page', type=int, default=DEFAULT_PAGE)
        parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)

        parser.add_argument('username', type=str)
        parser.add_argument('yulecheng', type=str)
        parser.add_argument('TimeLower', type=int)
        parser.add_argument('TimeUpper', type=int)
        parser.add_argument('amountLower', type=int)
        parser.add_argument('amountUpper', type=int)
        parser.add_argument('state', type=str)
        parser.add_argument('buquan', type=int)
        args = parser.parse_args(strict=True)

        criterion = set()
        criterion.add(and_(EntertainmentCityTradeLog.state != 0, EntertainmentCityTradeLog.state != 1))
        if 'buquan' in args and args['buquan'] is not None:
            if args['buquan'] == 1:
                criterion.add(EntertainmentCityTradeLog.state == 3)
                if 'username' in args and args['username'] is not None:
                    criterion.add(EntertainmentCityTradeLog.username == args['username'])

                if 'yulecheng' in args and args['yulecheng'] is not None:
                    ylcname = args['yulecheng'].split(',')
                    criterion.add(
                        or_(EntertainmentCityTradeLog.ec.in_(ylcname), EntertainmentCityTradeLog.last_ec.in_(ylcname)))

                if 'TimeLower' in args and args['TimeLower'] is not None:
                    criterion.add(EntertainmentCityTradeLog.actionTime >= args['TimeLower'])

                if 'TimeUpper' in args and args['TimeUpper'] is not None:
                    criterion.add(EntertainmentCityTradeLog.actionTime <= args['TimeUpper'])

                if 'amountLower' in args and args['amountLower'] is not None:
                    criterion.add(EntertainmentCityTradeLog.amount >= args['amountLower'])

                if 'amountUpper' in args and args['amountUpper'] is not None:
                    criterion.add(EntertainmentCityTradeLog.amount <= args['amountUpper'])
        else:

            if 'username' in args and args['username'] is not None:
                criterion.add(EntertainmentCityTradeLog.username == args['username'])

            if 'yulecheng' in args and args['yulecheng'] is not None:
                ylcname = args['yulecheng'].split(',')
                criterion.add(or_(EntertainmentCityTradeLog.ec.in_(ylcname),EntertainmentCityTradeLog.last_ec.in_(ylcname)))

            if 'TimeLower' in args and args['TimeLower'] is not None:
                criterion.add(EntertainmentCityTradeLog.actionTime >= args['TimeLower'])

            if 'TimeUpper' in args and args['TimeUpper'] is not None:
                criterion.add(EntertainmentCityTradeLog.actionTime <= args['TimeUpper'])

            if 'amountLower' in args and args['amountLower'] is not None:
                criterion.add(EntertainmentCityTradeLog.amount >= args['amountLower'])

            if 'amountUpper' in args and args['amountUpper'] is not None:
                criterion.add(EntertainmentCityTradeLog.amount <= args['amountUpper'])

            if 'state' in args and args['state'] is not None:
                state = args['state'].split(',')
                criterion.add(or_(EntertainmentCityTradeLog.state.in_(state)))

        query = db.session.query(
            EntertainmentCityTradeLog.id,
            EntertainmentCityTradeLog.uid,
            EntertainmentCityTradeLog.username,
            EntertainmentCityTradeLog.operator,
            EntertainmentCityTradeLog.ec,
            EntertainmentCityTradeLog.last_ec,
            EntertainmentCityTradeLog.actionTime,
            EntertainmentCityTradeLog.amount,
            EntertainmentCityTradeLog.state,
            EntertainmentCityTradeLog.type,
            EntertainmentCityTradeLog.orderid,
             ).order_by(EntertainmentCityTradeLog.actionTime.desc())
        result = []
        pagination = paginate(query, criterion, args['page'], args['pageSize'])
        for item in pagination.items:
            result.append({
                'id':item.id,
                'uid':item.uid,
                'username':item.username,
                'ec':item.ec,
                'last_ec': item.last_ec,
                'actionTime':item.actionTime,
                'amount':item.amount,
                'state':item.state,
                'type':item.type,
                'operator':item.operator,
                'orderid':item.orderid
            })
        return make_response(result, page=pagination.page, pages=pagination.pages, total=pagination.total)



class TransferLogDetail(Resource):

    def get(self):
        parser = RequestParser(trim=True)
        parser.add_argument('orderid', type=int)
        args = parser.parse_args()

        query = db.session.query(
            EntertainmentCityTradeLog.uid,
            EntertainmentCityTradeLog.username,
            EntertainmentCityTradeLog.amount,
            EntertainmentCityTradeLog.actionTime,
            EntertainmentCityTradeLog.state,
            EntertainmentCityTradeLog.ec,
            EntertainmentCityTradeLog.last_ec,
            EntertainmentCityTradeLog.operator,
            EntertainmentCityTradeLog.orderid,

            ).filter(and_(EntertainmentCityTradeLog.orderid == args['orderid'],EntertainmentCityTradeLog.state != 1,EntertainmentCityTradeLog.state != 0)).all()
        result = []
        data = {}
        for arg in query:
            data["uid"] = arg.uid
            data["username"] = arg.username
            data["amount"] = arg.amount
            data["actionTime"] = arg.actionTime
            data["state"] = arg.state
            data["ec"] = arg.ec
            data["last_ec"] = arg.last_ec
            data["operator"] = arg.operator
            data['orderid'] = arg.orderid
            result.append(data)

        return make_response(result)

    '''确认额度'''

    def put(self):

        parser = RequestParser(trim=True)
        parser.add_argument('orderid', type=int, required=True)
        parser.add_argument('state', type=int, required=True)
        parser.add_argument('amount', type=float, required=True)
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('uid', type=int, required=True)
        args = parser.parse_args()

        user = User.query.get(g.current_user.id)

        # if user.systemDepositLimitOnce is not None:
        #     if args['amount'] > user.systemDepositLimitOnce:
        #         return jsonify({
        #             'success': False,
        #             'errorCode': 403,
        #             'errorMsg': '超出单次存款上限'
        #         })
        # if user.systemDepositLimitCount is not None:
        #     if user.systemDepositLimitTotal == None:
        #         user.systemDepositLimitTotal = 0
        #     if args['amount'] > user.systemDepositLimitCount - user.systemDepositLimitTotal:
        #         return jsonify({
        #             'success': False,
        #             'errorCode': 403,
        #             'errorMsg': '超出您的总存入限额'
        #         })
        try:
            member = Member.query.get(args['uid'])
            if member:
                # 会员加钱
                member.balance += args['amount']
                db.session.add(member)
                # db.session.commit()

                # # 管理员-总存款限额
                # if user.systemDepositLimitTotal == None:
                #     user.systemDepositLimitTotal = 0
                # user.systemDepositLimitTotal += args['amount']
                # db.session.add(user)

                # 会员存款记录
                deposit = Deposit()
                if 'uid' in args and args['uid'] is not None:
                    deposit.memberId = args['uid']

                if 'amount' in args and args['amount'] is not None:
                    deposit.depositAmount = args['amount']

                if 'orderid' in args and args['orderid'] is not None:
                    deposit.number = str(args['orderid'])

                deposit.auditUser = user.id
                deposit.auditTime = time_to_value()
                deposit.auditHost = host_to_value(request.remote_addr)
                deposit.isAcdemen = 0
                deposit.type = 900011
                if 'username' in args and args['username'] is not None:
                    deposit.username = args['username']
                deposit.applicationAmount = args['amount']
                deposit.applicationTime = time_to_value()
                deposit.applicationHost = host_to_value(request.remote_addr)
                deposit.status = 2
                deposit.isDelete = 0
                deposit.flag = 0
                db.session.add(deposit)
                # db.session.commit()


                # # 账变信息

                cion = MemberAccountChangeRecord()
                cion.memberId = args['uid']
                cion.amount = args['amount']
                cion.orderId = args['orderid']
                cion.accountChangeType = 900011
                cion.actionUID = user.id
                cion.OperatorName = user.username
                cion.time = time_to_value()
                cion.host = host_to_value(request.remote_addr)
                cion.isAcdemen = 0
                cion.memberBalance = member.balance + deposit.depositAmount
                cion.memberFrozenBalance = member.frozenBalance
                cion.info = '额度转账确认'
                db.session.add(cion)
                # db.session.commit()

                # 管理员操作记录
                optionhistory = OperationHistory()
                optionhistory.uid = member.id
                optionhistory.info = '转账额度确认%f'% args['amount']
                optionhistory.username = member.username
                optionhistory.auditime = time_to_value()
                optionhistory.makeUser = g.current_user.id
                optionhistory.makeUserName = user.username
                optionhistory.ip = host_to_value(request.remote_addr)
                db.session.add(optionhistory)
                # db.session.commit()

                result = db.session.query(EntertainmentCityTradeLog).filter(EntertainmentCityTradeLog.orderid == args['orderid']).first()
                if 'state' in args and args['state'] is not None:
                    # 修改转账额度确认状态
                    result.state = args['state']
                    result.operator = g.current_user.username
                    result.actionTime = time_to_value()
                    db.session.add(result)
            db.session.commit()

        except:
            db.session.rollback()
            db.session.remove()
            abort(500)

        return {'success': True,'message':'手动补全额度成功'}


class GetEntertainmentCityListAll(Resource):
    def get(self):
        result = EntertainmentCity().getListAll()
        result = dict(result)
        result['AG'] = result['AG'].split(',')
        result['PT'] = result['PT'].split(',')
        result['KAIYUAN'] = result['KAIYUAN'].split(',')
        result['kk'] = result['kk'].split(',')
        return result

class GetEntertainmentCityListone(Resource):
    def get(self):
        return {
            1001: '彩票',
            1002: '视讯',
            1003: '棋牌',
            1004: '电子',
            1005: '体育',
            1006: '捕鱼',

        }
