from flask_restful import request,Resource, marshal_with, fields
from flask_restful.reqparse import RequestParser
from app.models.dictionary import Dictionary
from app.models.blast_bets import BlastBets,BlastBetsCredit
from app.models.blast_type import BlastType
from app.models.blast_lhc_ratio import BlastLHCRatio
from app.models.blast_played_group import BlastPlayedGroup,BlastPlayedGroupCredit
from ..parsers.lotteryParsers import bets_parsers,type_parsers,played_group_parsers,played_parser,played_group_credit_parsers,played_credit_parser
from app.api_0_1.common.utils import make_marshal_fields,make_response,make_response_from_pagination
import json
from app.models.blast_played import *
from app.models import *
from app.models.blast_type import BlastType
from app.models.entertainment_city_bets_detail import EntertainmentCityBetsDetail
from app.models.member import Member
from sqlalchemy.sql import union,union_all
from sqlalchemy.orm import aliased
from sqlalchemy import func,and_,or_
from sqlalchemy import literal
from app.models.common.utils import *
from app.models.entertainment_city import EntertainmentCity
import ast
from app.models.dictionary import Dictionary
from app.common.dataUtils import changeData_str
import os
from openpyxl import Workbook
from app.common.utils import *
from ..common import *
from ..common.utils import *

'''
彩票api
'''

dictionary_fields = {
    'data': fields.List(fields.Nested({
        'type': fields.String,
        'code': fields.Integer,
        'name': fields.String,
        'remark': fields.String,
        
    })),
    'success': fields.Boolean(default=True),
}

'''
彩票的分组
'''
class LotteryGroupAPI(Resource):
    @marshal_with(dictionary_fields)
    def get(self):
        results = Dictionary.getDataByType(100103)
        return {
            'data': results,
        }
        
'''
投注页面显示时分组
'''
class LotteryDefaultViewGroupAPI(Resource):
    @marshal_with(dictionary_fields)
    def get(self):
        results = Dictionary.getDataByType(100102)
        return {
            'data': results,
        }

'''
投注记录
'''
class BetsRecordAPI(Resource):

    def get(self):
        m_args = bets_parsers.parse_args(strict=True)
        ci = db.session.query(EntertainmentCity.code).filter(EntertainmentCity.enable == 1).all()
        criterin = self.getCondition(m_args)

        # if m_args['playerId'] is not None:
        #     for t in m_args['playerId']:
        #         if (t,) not in ci:
        #             return make_response(error_code=400, error_message="暂不支持此平台")
        # else:
        #     return make_response([])

        if m_args['playerId'] is None and m_args['historyBet'] != 1:
            return make_response([])


        criterin_bets = criterin['criterin_bets']
        criterin_credit = criterin['criterin_credit']
        criterin_city = criterin['criterin_city']
        q1 = db.session.query(
            Member.username,
        ).filter(Member.isTsetPLay == 0)
        criterin_bets.add(
            BlastBets.username.in_(q1)
        )
        if m_args['status'] == 1:
            criterin_bets.add(BlastBets.state == 1)
        else:
            criterin_bets.add(BlastBets.state == 2)
        criterin_credit.add(
            BlastBetsCredit.memberUsername.in_(q1)

        )
        if m_args['status'] == 1:
            criterin_credit.add(BlastBetsCredit.state == 1)
        else:
            criterin_credit.add(BlastBetsCredit.state == 2)

        criterin_city.add(EntertainmentCityBetsDetail.PlayerName.in_(q1))

        if m_args['playerIdType'] is not None:
            playerIdType = ast.literal_eval(m_args['playerIdType'])
            # qq = db.session.query(
            #     EntertainmentCityBetsDetail.PlayerName.label('PlayerName'),
            #     func.concat(EntertainmentCityBetsDetail.ECCode - EntertainmentCityBetsDetail.childType).label(
            #         'gameType')
            # ).subquery()
            # cit = db.session.query(
            #     qq.c.PlayerName
            # ).filter(qq.c.gameType.in_(playerIdType))
            criterin_city.add(func.concat(EntertainmentCityBetsDetail.ECCode,'-',EntertainmentCityBetsDetail.childType).in_(playerIdType))
        criterin = {}
        criterin['criterin_bets'] = criterin_bets
        criterin['criterin_credit'] = criterin_credit
        criterin['criterin_city'] = criterin_city
        # 判断是否是从历史记录过来的
        if m_args['historyBet'] == 1:
            betsprofitandloss = self.getKKandYlc(criterin)

        #游戏类型
        if m_args['playerId'] is not None:
        # 获取ylc和kk
            if ('AG' in m_args['playerId'] or 'PT' in m_args['playerId'] or 'KAIYUAN' in m_args['playerId']) and ('KK' in m_args['playerId'] or 'kk' in m_args['playerId']):

                betsprofitandloss = self.getKKandYlc(criterin)
            else:
                if 'kk' in m_args['playerId'] or 'KK' in m_args['playerId']:

                    # 获取KK
                    betsprofitandloss = self.getKK(criterin)
                else:
                    # 获取ylc

                    betsprofitandloss = self.getYlc(criterin)


        pagination = paginate_one(betsprofitandloss,m_args['page'], m_args['pageSize'])
        result = []
        for items_one in pagination.items:
            result.append({
                'orderId': items_one.orderId,
                'memberId': items_one.memberId,
                'memberUsername': items_one.memberUsername,
                'playGame': items_one.playGame,
                'payTime': items_one.payTime,
                'betTime': items_one.betTime,
                'betAmount': float(items_one.betAmount),
                'betAmountYX': float(items_one.betAmountYX),
                'paicai': float(items_one.paicai),
                'ECCode': items_one.ECCode,
                'gameType': str(items_one.gameType),
                'gameTypeNum':items_one.gameTypeNum,
                'enable': items_one.state,
            })
        return make_response(result,
                             page=pagination.page, pages=pagination.pages, total=pagination.total,
                             totalBalance=m_args['page'], totalRebate=m_args['pageSize']
                             )


    def getCondition(self,m_args):
        criterin_bets = set()
        criterin_credit = set()
        criterin_city = set()
        if m_args['memberId'] is not None:
            criterin_bets.add(BlastBets.username == m_args['memberId'])
            criterin_credit.add(BlastBetsCredit.memberUsername == m_args['memberId'])
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName == m_args['memberId'])
        if m_args['agentsId'] is not None:
            uids = db.session.query(Member.username).filter(func.find_in_set(m_args['agentsId'],Member.parentsInfo)).all()
            uid_res = []
            for uid in uids:
                uid_res.append(uid[0])
            criterin_bets.add(BlastBets.username.in_(uid_res))
            criterin_credit.add(BlastBetsCredit.memberUsername.in_(uid_res))
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName.in_(uid_res))
        if m_args['betTimeLower'] is not None:
            criterin_bets.add(BlastBets.actionTime >= m_args['betTimeLower'])
            criterin_credit.add(BlastBetsCredit.betTime >= m_args['betTimeLower'])
            criterin_city.add(EntertainmentCityBetsDetail.BetTime >= m_args['betTimeLower'])
        if m_args['betTimeUpper'] is not None:
            criterin_bets.add(BlastBets.actionTime <= m_args['betTimeUpper'])
            criterin_credit.add(BlastBetsCredit.betTime <= m_args['betTimeUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.BetTime <= m_args['betTimeUpper'])
        if m_args['payoutTimeLower'] is not None:
            criterin_bets.add(BlastBets.kjTime >= m_args['payoutTimeLower'])
            criterin_credit.add(BlastBetsCredit.drawTime >= m_args['payoutTimeLower'])
            criterin_city.add(EntertainmentCityBetsDetail.ReckonTime >= m_args['payoutTimeLower'])
        if m_args['payoutTimeUpper'] is not None:
            criterin_bets.add(BlastBets.kjTime <= m_args['payoutTimeUpper'])
            criterin_credit.add(BlastBetsCredit.drawTime <= m_args['payoutTimeUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.ReckonTime <= m_args['payoutTimeUpper'])

        if m_args['betnumber'] is not None:
            criterin_bets.add(BlastBets.wjorderId == m_args['betnumber'])
            criterin_credit.add(BlastBetsCredit.orderId == m_args['betnumber'])
            criterin_city.add(EntertainmentCityBetsDetail.BillNo == m_args['betnumber'])
        if m_args['gameId'] is not None:
            criterin_bets.add(BlastBets.playedId == m_args['gameId'])
            criterin_credit.add(BlastBetsCredit.gameIssue == m_args['gameId'])
            criterin_city.add(EntertainmentCityBetsDetail.GameCode == m_args['gameId'])
        if m_args['gameName'] is not None:
            res = db.session.query(BlastType.id).filter(BlastType.title == m_args['gameName']).first()
            if res is not None:
                res = res[0]
            criterin_bets.add(BlastBets.type == res)
            criterin_credit.add(BlastBetsCredit.gameType == res)
            criterin_city.add(EntertainmentCityBetsDetail.GameTypeInfo == m_args['gameName'])
        if m_args['gameNameLike'] is not None:
            res = db.session.query(BlastType.id).filter(BlastType.title .like('%' + m_args['gameNameLike']  + '%')).all()
            res_in = []
            if res is not None:
                for res_one in res:
                    res_in.append(res_one[0])
            else:
                res_in = []
            criterin_bets.add(BlastBets.type.in_(res_in))
            criterin_credit.add(BlastBetsCredit.gameType.in_(res_in))
            criterin_city.add(EntertainmentCityBetsDetail.GameTypeInfo.like('%' + m_args['gameNameLike']  + '%'))
        if m_args['status'] is not None:
            criterin_bets.add(BlastBets.state == m_args['status'])
            criterin_credit.add(BlastBetsCredit.state == m_args['status'])
            criterin_city.add(EntertainmentCityBetsDetail.Flag != m_args['status'])
        if m_args['betAmountLower'] is not None:
            criterin_bets.add((BlastBets.mode*BlastBets.actionNum*BlastBets.beiShu) >= m_args['betAmountLower'])
            criterin_credit.add(BlastBetsCredit.betAmount >= m_args['betAmountLower'])
            criterin_city.add(EntertainmentCityBetsDetail.BetAmount >= m_args['betAmountLower'])
        if m_args['betAmountUpper'] is not None:
            criterin_bets.add((BlastBets.mode*BlastBets.actionNum*BlastBets.beiShu) <= m_args['betAmountUpper'])
            criterin_credit.add(BlastBetsCredit.betAmount <= m_args['betAmountUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.BetAmount <= m_args['betAmountUpper'])
        if m_args['betAmountLowerYx'] is not None:
            criterin_bets.add(and_((BlastBets.mode*BlastBets.actionNum*BlastBets.beiShu) >= m_args['betAmountLowerYx'],BlastBets.state == 2))
            criterin_credit.add(and_(BlastBetsCredit.betAmount >= m_args['betAmountLowerYx'],BlastBetsCredit.state == 2))
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName >= m_args['betAmountLowerYx'])
        if m_args['betAmountUpperYx'] is not None:
            criterin_bets.add(and_((BlastBets.mode*BlastBets.actionNum*BlastBets.beiShu) <= m_args['betAmountUpperYx'],BlastBets.state == 2))
            criterin_credit.add(and_(BlastBetsCredit.betAmount <= m_args['betAmountUpperYx'],BlastBetsCredit.state == 2))
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName <= m_args['betAmountUpperYx'])
        if m_args['payoutAmountLower'] is not None:
            criterin_bets.add(BlastBets.bonus >= m_args['payoutAmountLower'])
            criterin_credit.add(BlastBetsCredit.bonus >= m_args['payoutAmountLower'])
            criterin_city.add(EntertainmentCityBetsDetail.CusAccount >= m_args['payoutAmountLower'])
        if m_args['payoutAmountUpper'] is not None:
            criterin_bets.add(BlastBets.bonus <= m_args['payoutAmountUpper'])
            criterin_credit.add(BlastBetsCredit.bonus <= m_args['payoutAmountUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.CusAccount <= m_args['payoutAmountUpper'])

        criterin = {}
        criterin['criterin_bets'] =  criterin_bets
        criterin['criterin_credit'] =  criterin_credit
        criterin['criterin_city'] =  criterin_city
        return criterin

    def getKK(self, criterin):
        criterin_bets = criterin['criterin_bets']
        criterin_credit = criterin['criterin_credit']

        q5 = db.session.query(
            BlastBets.wjorderId.label('orderId'),
            BlastBets.uid.label('memberId'),
            BlastBets.username.label('memberUsername'),
            BlastType.title.label('playGame'),
            BlastBets.kjTime.label('payTime'),
            BlastBets.actionTime.label('betTime'),
            (BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu).label('betAmount'),
            BlastBets.bonus.label('paicai'),
            literal('KK').label('ECCode'),
            literal('1001').label('gameType'),
            literal('300').label('gameTypeNum'),
            BlastBets.state.label('state'),
        ).filter(*criterin_bets)
        q5 = q5.outerjoin(BlastType, BlastType.id == BlastBets.type)

        q6 = db.session.query(
            BlastBetsCredit.orderId.label('orderId'),
            BlastBetsCredit.memberId.label('memberId'),
            BlastBetsCredit.memberUsername.label('memberUsername'),
            BlastType.title.label('playGame'),
            BlastBetsCredit.drawTime.label('payTime'),
            BlastBetsCredit.betTime.label('betTime'),
            BlastBetsCredit.betAmount.label('betAmount'),
            BlastBetsCredit.bonus.label('paicai'),
            literal('KK').label('ECCode'),
            literal('1001').label('gameType'),
            literal('101').label('gameTypeNum'),
            BlastBetsCredit.state.label('state'),
        ).filter(*criterin_credit)
        q6 = q6.outerjoin(BlastType, BlastType.id == BlastBetsCredit.gameType)

        res = union_all(q5, q6)
        user_alias_s = aliased(res, name='user_alias_s')
        betsprofitandloss = db.session.query(
            user_alias_s.c.orderId.label('orderId'),
            user_alias_s.c.memberId.label('memberId'),
            user_alias_s.c.memberUsername.label('memberUsername'),
            user_alias_s.c.playGame.label('playGame'),
            user_alias_s.c.payTime.label('payTime'),
            user_alias_s.c.betTime.label('betTime'),
            user_alias_s.c.betAmount.label('betAmount'),
            user_alias_s.c.betAmount.label('betAmountYX'),
            user_alias_s.c.paicai.label('paicai'),
            user_alias_s.c.ECCode.label('ECCode'),
            user_alias_s.c.gameType.label('gameType'),
            user_alias_s.c.gameTypeNum.label('gameTypeNum'),
            user_alias_s.c.state.label('state'),
        ).order_by(user_alias_s.c.payTime.desc())

        return betsprofitandloss

    def getYlc(self, criterin):
        criterin_city = criterin['criterin_city']

        q7 = db.session.query(
            EntertainmentCityBetsDetail.BillNo.label('orderId'),
            Member.id.label('memberId'),
            EntertainmentCityBetsDetail.PlayerName.label('memberUsername'),
            EntertainmentCityBetsDetail.GameTypeInfo.label('playGame'),
            EntertainmentCityBetsDetail.ReckonTime.label('payTime'),
            EntertainmentCityBetsDetail.BetTime.label('betTime'),
            EntertainmentCityBetsDetail.ValidBetAmount.label('betAmount'),
            EntertainmentCityBetsDetail.ValidBetAmount.label('betAmountYX'),
            EntertainmentCityBetsDetail.CusAccount.label('paicai'),
            EntertainmentCityBetsDetail.ECCode.label('ECCode'),
            EntertainmentCityBetsDetail.childType.label('gameType'),
            literal('200').label('gameTypeNum'),
            EntertainmentCityBetsDetail.Flag.label('state'),
        ).filter(*criterin_city).order_by(EntertainmentCityBetsDetail.ReckonTime.desc())
        q7 = q7.outerjoin(Member, Member.username == EntertainmentCityBetsDetail.PlayerName)

        return q7

    def getKKandYlc(self, criterin):
        criterin_bets = criterin['criterin_bets']
        criterin_credit = criterin['criterin_credit']
        criterin_city = criterin['criterin_city']

        q5 = db.session.query(
            BlastBets.wjorderId.label('orderId'),
            BlastBets.uid.label('memberId'),
            BlastBets.username.label('memberUsername'),
            BlastType.title.label('playGame'),
            BlastBets.kjTime.label('payTime'),
            BlastBets.actionTime.label('betTime'),
            (BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu).label('betAmount'),
            BlastBets.bonus.label('paicai'),
            literal('KK').label('ECCode'),
            literal('1001').label('gameType'),
            literal('300').label('gameTypeNum'),
            BlastBets.state.label('state'),
        ).filter(*criterin_bets)
        q5 = q5.outerjoin(BlastType, BlastType.id == BlastBets.type)



        q6 = db.session.query(
            BlastBetsCredit.orderId.label('orderId'),
            BlastBetsCredit.memberId.label('memberId'),
            BlastBetsCredit.memberUsername.label('memberUsername'),
            BlastType.title.label('playGame'),
            BlastBetsCredit.drawTime.label('payTime'),
            BlastBetsCredit.betTime.label('betTime'),
            BlastBetsCredit.betAmount.label('betAmount'),
            BlastBetsCredit.bonus.label('paicai'),
            literal('KK').label('ECCode'),
            literal('1001').label('gameType'),
            literal('101').label('gameTypeNum'),
            BlastBetsCredit.state.label('state'),
        ).filter(*criterin_credit)
        q6 = q6.outerjoin(BlastType, BlastType.id == BlastBetsCredit.gameType)



        q7 = db.session.query(
            EntertainmentCityBetsDetail.BillNo.label('orderId'),
            Member.id.label('memberId'),
            EntertainmentCityBetsDetail.PlayerName.label('memberUsername'),
            EntertainmentCityBetsDetail.GameTypeInfo.label('playGame'),
            EntertainmentCityBetsDetail.ReckonTime.label('payTime'),
            EntertainmentCityBetsDetail.BetTime.label('betTime'),
            EntertainmentCityBetsDetail.ValidBetAmount.label('betAmount'),
            EntertainmentCityBetsDetail.CusAccount.label('paicai'),
            EntertainmentCityBetsDetail.ECCode.label('ECCode'),
            EntertainmentCityBetsDetail.childType.label('gameType'),
            literal('200').label('gameTypeNum'),
            literal('2').label('state'),
        ).filter(*criterin_city)
        q7 = q7.outerjoin(Member, Member.username == EntertainmentCityBetsDetail.PlayerName)

        res = union_all(q5, q6, q7)
        user_alias_s = aliased(res, name='user_alias_s')
        betsprofitandloss = db.session.query(
            user_alias_s.c.orderId.label('orderId'),
            user_alias_s.c.memberId.label('memberId'),
            user_alias_s.c.memberUsername.label('memberUsername'),
            user_alias_s.c.playGame.label('playGame'),
            user_alias_s.c.payTime.label('payTime'),
            user_alias_s.c.betTime.label('betTime'),
            user_alias_s.c.betAmount.label('betAmount'),
            user_alias_s.c.betAmount.label('betAmountYX'),
            user_alias_s.c.paicai.label('paicai'),
            user_alias_s.c.ECCode.label('ECCode'),
            user_alias_s.c.gameType.label('gameType'),
            user_alias_s.c.gameTypeNum.label('gameTypeNum'),
            user_alias_s.c.state.label('state'),
        ).order_by(user_alias_s.c.payTime.desc())

        return betsprofitandloss


'''
投注记录详情
'''
class BetsRecordAPIInfos(Resource):

    def get(self):
        bets_parsers_infos = RequestParser()
        bets_parsers_infos.add_argument('Eccode', type=str, location=['form', 'json', 'args'])
        bets_parsers_infos.add_argument('orderId', type=str, location=['form', 'json', 'args'])
        bets_parsers_infos.add_argument('gameTypeNum', type=int, location=['form', 'json', 'args'])
        bets_parsers_infos.add_argument('historyBet', type=int, location=['form', 'json', 'args'])
        m_args = bets_parsers_infos.parse_args(strict=True)
        if m_args['orderId'] is None:
            return ({
				'success': False,
				'errorCode': 403,
				'errorMsg': '请输入订单号'
			})
        if m_args['Eccode'] is None:
            return ({
                'success': False,
                'errorCode': 403,
                'errorMsg': '查询错误'
            })
        critern_city = set()
        critern_kk_bet = set()
        critern_kk_credit = set()
        if m_args['orderId'] is not None:
            critern_city.add(EntertainmentCityBetsDetail.BillNo == m_args['orderId'])
            critern_kk_bet.add(BlastBets.wjorderId == m_args['orderId'])
            critern_kk_credit.add(BlastBetsCredit.orderId == m_args['orderId'])
        # 当查询的交易记录是娱乐城的时候
        if m_args['Eccode'] == 'AG' or m_args['Eccode'] == 'PT' or m_args['Eccode'] == 'KAIYUAN':
            m_args_one = EntertainmentCityBetsDetail().getCityInfo(critern_city)
            if m_args_one:
                m_args_one = m_args_one[0]
                # 判断是否是从历史记录过来的
                if m_args['historyBet'] == 1:
                    result = {
                        'memberId': m_args_one.memberId,
                        'PlayerName': m_args_one.PlayerName,
                        'ECCode': m_args_one.ECCode,
                        'childType': m_args_one.childType,
                        'PlayTypeInfo': m_args_one.PlayTypeInfo,
                        'BetTime': m_args_one.BetTime,
                        'BetAmount': m_args_one.BetAmount,
                        'ReckonTime': m_args_one.ReckonTime,
                        'CusAccount': m_args_one.CusAccount,
                        'ValidBetAmount': m_args_one.ValidBetAmount
                    }
                else:

                    result = {
                        'memberId': m_args_one.memberId,
                        'PlayerName': m_args_one.PlayerName,
                        'ECCode': m_args_one.ECCode,
                        'childType' :m_args_one.childType,
                        'GameTypeInfo': m_args_one.GameTypeInfo,
                        'BetTime': m_args_one.BetTime,
                        'BetAmount': m_args_one.BetAmount,
                        'ReckonTime': m_args_one.ReckonTime,
                        'CusAccount': m_args_one.CusAccount,
                        'ValidBetAmount': m_args_one.ValidBetAmount,
                        'detail':{
                            'BillNo' : m_args_one.BillNo,
                            'PlayerName': m_args_one.PlayerName,
                            'ECCode': m_args_one.ECCode,
                            'childType': m_args_one.childType,
                            'BetTime': m_args_one.BetTime,
                            'BetAmount': m_args_one.BetAmount,
                            'ReckonTime': m_args_one.ReckonTime,
                            'CusAccount': m_args_one.CusAccount,
                            'ValidBetAmount': m_args_one.ValidBetAmount,
                            'GameCodeInfo' : m_args_one.GameCodeInfo,
                            'GameName' : m_args_one.GameName,
                            'PlayTypeInfo' : m_args_one.PlayTypeInfo,
                            'GameTypeInfo': m_args_one.GameTypeInfo,
                            'MachineType' : m_args_one.MachineType,
                            'NetAmount' : m_args_one.NetAmount,
                            'BeforeCredit' : m_args_one.BeforeCredit,
                            'Balance' : m_args_one.Balance,
                            'RoomID' : m_args_one.RoomID,
                            'ProductID' : m_args_one.ProductID,
                            'ExttxID' : m_args_one.ExttxID,
                            'Flag' : m_args_one.Flag,
                            'Currency' : m_args_one.Currency,
                            'TableCode' : m_args_one.TableCode,
                            'BetIP' : m_args_one.BetIP,
                            'RecalcuTime' : m_args_one.RecalcuTime,
                            'PlatformType' : m_args_one.PlatformType,
                            'Remark' : m_args_one.Remark,
                            'Round' : m_args_one.Round
                        }
                    }
                    # result['detail'] = ast.literal_eval(result['detail'])
                    # result['detail']['ECCode'] = result['ECCode']
                    result['detail'] = json.dumps(result['detail'])
            else:
                result = {}
        # 当查询的记录是KK的时候

        elif m_args['Eccode'] == 'KK':
            if m_args['gameTypeNum'] is None:
                m_args_one = []
                result = {}
            if m_args['gameTypeNum'] == 300:
                gameTypeName = '(官)'
                m_args_one = BlastBets().getBetInfo(critern_kk_bet)
            elif m_args['gameTypeNum'] == 101:
                gameTypeName = '(信)'
                m_args_one = BlastBetsCredit().getCreditInfo(critern_kk_credit)
            if m_args_one:
                if m_args['historyBet'] == 1:
                    m_args_one = m_args_one[0]
                    result = {
                        'memberId': m_args_one.memberId,
                        'PlayerName': m_args_one.PlayerName,
                        'ECCode': m_args_one.ECCode,
                        'childType': m_args_one.childType,
                        'PlayTypeInfo': m_args_one.PlayTypeInfo,
                        'BetTime': m_args_one.BetTime,
                        'BetAmount': float(m_args_one.BetAmount),
                        'ReckonTime': m_args_one.ReckonTime,
                        'CusAccount': float(m_args_one.CusAccount),
                        'ValidBetAmount': float(m_args_one.ValidBetAmount)

                    }
                else:
                    m_args_one = m_args_one[0]
                    result = {
                        'memberId': m_args_one.memberId,

                        'PlayerName': m_args_one.PlayerName,
                        'ECCode': m_args_one.ECCode,
                        'childType' :m_args_one.childType,
                        'PlayTypeInfo': m_args_one.PlayTypeInfo,
                        'BetTime': m_args_one.BetTime,
                        'BetAmount': float(m_args_one.BetAmount),
                        'ReckonTime': m_args_one.ReckonTime,
                        'CusAccount': float(m_args_one.CusAccount),
                        'ValidBetAmount': float(m_args_one.ValidBetAmount),
                        'detail':{
                            'numberOrderId': m_args_one.numberOrderId,
                            'gameTypeName': gameTypeName,
                            'PlayerName' : m_args_one.PlayerName,
                            'ECCode' : m_args_one.ECCode,
                            'childType' : m_args_one.childType,
                            'PlayTypeInfo' : m_args_one.PlayTypeInfo,
                            'BetKKTime' : m_args_one.BetTime,
                            'BetKKAmount' : float(m_args_one.BetAmount),
                            'ReckonTime' : m_args_one.ReckonTime,
                            'CusAccount' : float(m_args_one.CusAccount),
                            'ValidBetAmount' :float(m_args_one.ValidBetAmount),
                            'qs' : m_args_one.qs,
                            'state' : m_args_one.state,
                            'wfmc' : m_args_one.wfmc,
                            'wfmcPlay': m_args_one.wfmcPlay,
                            'xznr' : m_args_one.xznr,
                            'hyIp' : m_args_one.hyIp,
                            'kjjg' : m_args_one.kjjg,
                            'pl' : float(m_args_one.pl),
                            'sfzj' : m_args_one.sfzj,
                            'bs': m_args_one.bs,
                            'zs': m_args_one.zs,
                            'fdian': m_args_one.fdian
                        }
                    }
                    result['detail'] = json.dumps(result['detail'])
            else:
                result = {}


        return make_response([result])
    
    
'''
获取投注记录的全部金额和笔数
'''

class BetsRecordAPIListTotal(Resource):
    def get(self):
        m_args = bets_parsers.parse_args(strict=True)
        ci = db.session.query(EntertainmentCity.code).filter(EntertainmentCity.enable == 1).all()
        criterin = self.getCondition(m_args)

        # if m_args['playerId'] is not None:
        #     for t in m_args['playerId']:
        #         if (t,) not in ci:
        #             return make_response(error_code=400, error_message="暂不支持此平台")
        # else:
        #     return make_response([])

        if m_args['playerId'] is None and m_args['historyBet'] != 1:
            return make_response([])



        criterin_bets = criterin['criterin_bets']
        criterin_credit = criterin['criterin_credit']
        criterin_city = criterin['criterin_city']
        q1 = db.session.query(
            Member.username,
        ).filter(Member.isTsetPLay == 0)
        criterin_bets.add(
                BlastBets.username.in_(q1)
        )
        if m_args['status'] == 1:
            criterin_bets.add(BlastBets.state == 1)
        else:
            criterin_bets.add(BlastBets.state == 2)
        criterin_credit.add(
            BlastBetsCredit.memberUsername.in_(q1)

        )
        if m_args['status'] == 1:
            criterin_credit.add(BlastBetsCredit.state == 1)
        else:
            criterin_credit.add(BlastBetsCredit.state == 2)

        criterin_city.add(EntertainmentCityBetsDetail.PlayerName.in_(q1))

        if m_args['playerIdType'] is not None:
            playerIdType = ast.literal_eval(m_args['playerIdType'])
            # qq = db.session.query(
            #     EntertainmentCityBetsDetail.PlayerName.label('PlayerName'),
            #     func.concat(EntertainmentCityBetsDetail.ECCode - EntertainmentCityBetsDetail.childType).label(
            #         'gameType')
            # ).subquery()
            # cit = db.session.query(
            #     qq.c.PlayerName
            # ).filter(qq.c.gameType.in_(playerIdType))
            criterin_city.add(func.concat(EntertainmentCityBetsDetail.ECCode,'-',EntertainmentCityBetsDetail.childType).in_(playerIdType))
        criterin = {}
        criterin['criterin_bets'] = criterin_bets
        criterin['criterin_credit'] = criterin_credit
        criterin['criterin_city'] = criterin_city
        # 判断是否是从历史记录过来的
        if m_args['historyBet'] == 1:
            betsprofitandloss = self.getKKandYlc(criterin)
        #游戏类型
        if m_args['playerId'] is not None:
        # 获取ylc和kk
            if ('AG' in m_args['playerId'] or 'PT' in m_args['playerId'] or 'KAIYUAN' in m_args['playerId']) and ('KK' in m_args['playerId'] or 'kk' in m_args['playerId']):

                betsprofitandloss = self.getKKandYlc(criterin)
            else:
                if 'kk' in m_args['playerId'] or 'KK' in m_args['playerId']:
                    # 获取KK
                    betsprofitandloss = self.getKK(criterin)
                else:
                    # 获取ylc
                    betsprofitandloss = self.getYlc(criterin)

        if betsprofitandloss:
            if betsprofitandloss.TotalNumber is None:
                TotalNumber = 0

            else:
                TotalNumber = betsprofitandloss.TotalNumber
            if betsprofitandloss.TotalAmount is None:
                TotalAmount = 0

            else:
                TotalAmount = betsprofitandloss.TotalAmount

            if betsprofitandloss.TotalPaicai is None:
                TotalPaicai = 0

            else:
                TotalPaicai = betsprofitandloss.TotalPaicai

        result = []
        result.append({
            'TotalNumber':float(TotalNumber),
            'TotalAmount': float(TotalAmount),
            'TotalPaicai': float(TotalPaicai)
        })
        return make_response(result)

    def getCondition(self, m_args):
        criterin_bets = set()
        criterin_credit = set()
        criterin_city = set()
        if m_args['memberId'] is not None:
            criterin_bets.add(BlastBets.username == m_args['memberId'])
            criterin_credit.add(BlastBetsCredit.memberUsername == m_args['memberId'])
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName == m_args['memberId'])
        if m_args['agentsId'] is not None:
            uids = db.session.query(Member.username).filter(func.find_in_set(m_args['agentsId'], Member.parentsInfo)).all()
            uid_res = []
            for uid in uids:
                uid_res.append(uid[0])
            criterin_bets.add(BlastBets.username.in_(uid_res))
            criterin_credit.add(BlastBetsCredit.memberUsername.in_(uid_res))
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName.in_(uid_res))
        if m_args['betTimeLower'] is not None:
            criterin_bets.add(BlastBets.actionTime >= m_args['betTimeLower'])
            criterin_credit.add(BlastBetsCredit.betTime >= m_args['betTimeLower'])
            criterin_city.add(EntertainmentCityBetsDetail.BetTime >= m_args['betTimeLower'])
        if m_args['betTimeUpper'] is not None:
            criterin_bets.add(BlastBets.actionTime <= m_args['betTimeUpper'])
            criterin_credit.add(BlastBetsCredit.betTime <= m_args['betTimeUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.BetTime <= m_args['betTimeUpper'])
        if m_args['payoutTimeLower'] is not None:
            criterin_bets.add(BlastBets.kjTime >= m_args['payoutTimeLower'])
            criterin_credit.add(BlastBetsCredit.drawTime >= m_args['payoutTimeLower'])
            criterin_city.add(EntertainmentCityBetsDetail.ReckonTime >= m_args['payoutTimeLower'])
        if m_args['payoutTimeUpper'] is not None:
            criterin_bets.add(BlastBets.kjTime <= m_args['payoutTimeUpper'])
            criterin_credit.add(BlastBetsCredit.drawTime <= m_args['payoutTimeUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.ReckonTime <= m_args['payoutTimeUpper'])

        if m_args['betnumber'] is not None:
            criterin_bets.add(BlastBets.wjorderId == m_args['betnumber'])
            criterin_credit.add(BlastBetsCredit.orderId == m_args['betnumber'])
            criterin_city.add(EntertainmentCityBetsDetail.BillNo == m_args['betnumber'])
        if m_args['gameId'] is not None:
            criterin_bets.add(BlastBets.actionNo == m_args['gameId'])
            criterin_credit.add(BlastBetsCredit.gameIssue == m_args['gameId'])
            criterin_city.add(EntertainmentCityBetsDetail.GameCode == m_args['gameId'])
        if m_args['gameName'] is not None:
            res = db.session.query(BlastType.id).filter(BlastType.title == m_args['gameName']).first()
            if res is not None:
                res = res[0]
            criterin_bets.add(BlastBets.type == res)
            criterin_credit.add(BlastBetsCredit.gameType == res)
            criterin_city.add(EntertainmentCityBetsDetail.GameTypeInfo == m_args['gameName'])
        if m_args['gameNameLike'] is not None:
            res = db.session.query(BlastType.id).filter(BlastType.title .like('%' + m_args['gameNameLike']  + '%')).all()
            res_in = []
            if res is not None:
                for res_one in res:
                    res_in.append(res_one[0])
            else:
                res_in = []
            criterin_bets.add(BlastBets.type.in_(res_in))
            criterin_credit.add(BlastBetsCredit.gameType.in_(res_in))
            criterin_city.add(EntertainmentCityBetsDetail.GameTypeInfo.like('%' + m_args['gameNameLike']  + '%'))
        if m_args['status'] is not None:
            criterin_bets.add(BlastBets.state == m_args['status'])
            criterin_credit.add(BlastBetsCredit.state == m_args['status'])
            criterin_city.add(EntertainmentCityBetsDetail.Flag != m_args['status'])
        if m_args['betAmountLower'] is not None:
            criterin_bets.add((BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu) >= m_args['betAmountLower'])
            criterin_credit.add(BlastBetsCredit.betAmount >= m_args['betAmountLower'])
            criterin_city.add(EntertainmentCityBetsDetail.BetAmount >= m_args['betAmountLower'])
        if m_args['betAmountUpper'] is not None:
            criterin_bets.add((BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu) <= m_args['betAmountUpper'])
            criterin_credit.add(BlastBetsCredit.betAmount <= m_args['betAmountUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.BetAmount <= m_args['betAmountUpper'])
        if m_args['betAmountLowerYx'] is not None:
            criterin_bets.add(
                and_((BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu) >= m_args['betAmountLowerYx'],
                     BlastBets.state == 2))
            criterin_credit.add(
                and_(BlastBetsCredit.betAmount >= m_args['betAmountLowerYx'], BlastBetsCredit.state == 2))
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName >= m_args['betAmountLowerYx'])
        if m_args['betAmountUpperYx'] is not None:
            criterin_bets.add(
                and_((BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu) <= m_args['betAmountUpperYx'],
                     BlastBets.state == 2))
            criterin_credit.add(
                and_(BlastBetsCredit.betAmount <= m_args['betAmountUpperYx'], BlastBetsCredit.state == 2))
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName <= m_args['betAmountUpperYx'])
        if m_args['payoutAmountLower'] is not None:
            criterin_bets.add(BlastBets.bonus >= m_args['payoutAmountLower'])
            criterin_credit.add(BlastBetsCredit.bonus >= m_args['payoutAmountLower'])
            criterin_city.add(EntertainmentCityBetsDetail.CusAccount >= m_args['payoutAmountLower'])
        if m_args['payoutAmountUpper'] is not None:
            criterin_bets.add(BlastBets.bonus <= m_args['payoutAmountUpper'])
            criterin_credit.add(BlastBetsCredit.bonus <= m_args['payoutAmountUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.CusAccount <= m_args['payoutAmountUpper'])

        criterin = {}
        criterin['criterin_bets'] = criterin_bets
        criterin['criterin_credit'] = criterin_credit
        criterin['criterin_city'] = criterin_city
        return criterin

    def getKK(self, criterin):
        criterin_bets = criterin['criterin_bets']
        criterin_credit = criterin['criterin_credit']

        q5 = db.session.query(
            BlastBets.orderId.label('orderId'),
            (BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu).label('betAmount'),
            (BlastBets.bonus).label('paicai'),
        ).filter(*criterin_bets)
        q5 = q5.outerjoin(BlastType, BlastType.id == BlastBets.type)

        q6 = db.session.query(
            BlastBetsCredit.orderId.label('orderId'),
            BlastBetsCredit.betAmount.label('betAmount'),
            BlastBetsCredit.bonus.label('paicai'),
        ).filter(*criterin_credit)
        q6 = q6.outerjoin(BlastType, BlastType.id == BlastBetsCredit.gameType)

        res = union_all(q5, q6)
        user_alias_s = aliased(res, name='user_alias_s')
        betsprofitandloss = db.session.query(
            func.count(user_alias_s.c.orderId).label('TotalNumber'),
            func.sum(user_alias_s.c.betAmount).label('TotalAmount'),
            func.sum(user_alias_s.c.paicai).label('TotalPaicai'),
        ).all()
        if betsprofitandloss:
            betsprofitandloss = betsprofitandloss[0]
        return betsprofitandloss

    def getYlc(self, criterin):
        criterin_city = criterin['criterin_city']
        q7 = db.session.query(
            func.count(EntertainmentCityBetsDetail.BillNo).label('TotalNumber'),
            func.sum(EntertainmentCityBetsDetail.ValidBetAmount).label('TotalAmount'),
            func.sum(EntertainmentCityBetsDetail.CusAccount).label('TotalPaicai'),
        ).filter(*criterin_city)
        q7 = q7.outerjoin(Member, Member.username == EntertainmentCityBetsDetail.PlayerName).all()
        if q7:
            q7 = q7[0]
        return q7

    def getKKandYlc(self, criterin):
        criterin_bets = criterin['criterin_bets']
        criterin_credit = criterin['criterin_credit']
        criterin_city = criterin['criterin_city']

        q5 = db.session.query(
            BlastBets.orderId.label('orderId'),
            (BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu).label('betAmount'),
            (BlastBets.bonus).label('paicai'),
        ).filter(*criterin_bets)
        q5 = q5.outerjoin(BlastType, BlastType.id == BlastBets.type)


        q6 = db.session.query(
            BlastBetsCredit.orderId.label('orderId'),
            BlastBetsCredit.betAmount.label('betAmount'),
            BlastBetsCredit.bonus.label('paicai'),
        ).filter(*criterin_credit)
        q6 = q6.outerjoin(BlastType, BlastType.id == BlastBetsCredit.gameType)



        q7 = db.session.query(
            EntertainmentCityBetsDetail.BillNo.label('orderId'),
            EntertainmentCityBetsDetail.ValidBetAmount.label('betAmount'),
            EntertainmentCityBetsDetail.CusAccount.label('paicai'),
        ).filter(*criterin_city)
        q7 = q7.outerjoin(Member, Member.username == EntertainmentCityBetsDetail.PlayerName)

        res = union_all(q5, q6, q7)
        user_alias_s = aliased(res, name='user_alias_s')
        betsprofitandloss = db.session.query(
            func.count(user_alias_s.c.orderId).label('TotalNumber'),
            func.sum(user_alias_s.c.betAmount).label('TotalAmount'),
            func.sum(user_alias_s.c.paicai).label('TotalPaicai'),
        ).all()
        if betsprofitandloss:
            betsprofitandloss = betsprofitandloss[0]
        return betsprofitandloss



'''
投注记录汇出
'''
class ExcelBetsRecordAPIList(Resource):
    def get(self):
        m_args = bets_parsers.parse_args(strict=True)
        ci = db.session.query(EntertainmentCity.code).filter(EntertainmentCity.enable == 1).all()
        criterin = self.getCondition(m_args)

        # if m_args['playerId'] is not None:
        #     for t in m_args['playerId']:
        #         if (t,) not in ci:
        #             return make_response(error_code=400, error_message="暂不支持此平台")
        # else:
        #     return make_response([])

        if m_args['playerId'] is None and m_args['historyBet'] != 1:
            return make_response([])



        criterin_bets = criterin['criterin_bets']
        criterin_credit = criterin['criterin_credit']
        criterin_city = criterin['criterin_city']
        q1 = db.session.query(
            Member.username,
        ).filter(Member.isTsetPLay == 0)
        criterin_bets.add(
                BlastBets.username.in_(q1)
        )
        if m_args['status'] == 1:
            criterin_bets.add(BlastBets.state == 1)
        else:
            criterin_bets.add(BlastBets.state == 2)
        criterin_credit.add(
            BlastBetsCredit.memberUsername.in_(q1)

        )
        if m_args['status'] == 1:
            criterin_credit.add(BlastBetsCredit.state == 1)
        else:
            criterin_credit.add(BlastBetsCredit.state == 2)

        criterin_city.add(EntertainmentCityBetsDetail.PlayerName.in_(q1))

        if m_args['playerIdType'] is not None:
            playerIdType = ast.literal_eval(m_args['playerIdType'])
            # qq = db.session.query(
            #     EntertainmentCityBetsDetail.PlayerName.label('PlayerName'),
            #     func.concat(EntertainmentCityBetsDetail.ECCode - EntertainmentCityBetsDetail.childType).label(
            #         'gameType')
            # ).subquery()
            # cit = db.session.query(
            #     qq.c.PlayerName
            # ).filter(qq.c.gameType.in_(playerIdType))
            criterin_city.add(func.concat(EntertainmentCityBetsDetail.ECCode,'-',EntertainmentCityBetsDetail.childType).in_(playerIdType))
        criterin = {}
        criterin['criterin_bets'] = criterin_bets
        criterin['criterin_credit'] = criterin_credit
        criterin['criterin_city'] = criterin_city
        # 判断是否是从历史记录过来的
        if m_args['historyBet'] == 1:
            betsprofitandloss = self.getKKandYlc(criterin)
        #游戏类型
        if m_args['playerId'] is not None:
        # 获取ylc和kk
            if ('AG' in m_args['playerId'] or 'PT' in m_args['playerId'] or 'KAIYUAN' in m_args['playerId']) and ('KK' in m_args['playerId'] or 'kk' in m_args['playerId']):

                betsprofitandloss = self.getKKandYlc(criterin)
            else:
                if 'kk' in m_args['playerId'] or 'KK' in m_args['playerId']:
                    # 获取KK
                    betsprofitandloss = self.getKK(criterin)
                else:
                    # 获取ylc
                    betsprofitandloss = self.getYlc(criterin)

        results = []
        for item in betsprofitandloss:
            results.append(
                (item[0],
                 item[1],
                 item[2],
                 changeData_str(item[3]),
                 changeData_str(item[4]),
                 item[5],
                 item[6],
                 item[7])
            )
        title = ['帐号', '类型', '游戏名称', '派彩时间', '投注时间', '投注', '有效投注', '派彩']
        workbook = Workbook()
        worksheet = workbook.active

        worksheet.append(title)
        worksheet.column_dimensions['A'].width = 20
        worksheet.column_dimensions['B'].width = 18
        worksheet.column_dimensions['C'].width = 20
        worksheet.column_dimensions['D'].width = 20
        worksheet.column_dimensions['E'].width = 20
        worksheet.column_dimensions['F'].width = 8
        worksheet.column_dimensions['G'].width = 8
        worksheet.column_dimensions['H'].width = 8
        for result in results:
            worksheet.append(result)
        filename = '历史投注记录-' + str(int(time.time())) + '.xlsx'
        workbook.save(os.path.join(current_app.static_folder, filename))
        return make_response([{
            'success': True,
            'resultFilename': filename,
        }])

    def getCondition(self, m_args):
        criterin_bets = set()
        criterin_credit = set()
        criterin_city = set()
        if m_args['memberId'] is not None:
            criterin_bets.add(BlastBets.username == m_args['memberId'])
            criterin_credit.add(BlastBetsCredit.memberUsername == m_args['memberId'])
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName == m_args['memberId'])
        if m_args['agentsId'] is not None:
            uids = db.session.query(Member.username).filter(func.find_in_set(m_args['agentsId'], Member.parentsInfo)).all()
            uid_res = []
            for uid in uids:
                uid_res.append(uid[0])
            criterin_bets.add(BlastBets.username.in_(uid_res))
            criterin_credit.add(BlastBetsCredit.memberUsername.in_(uid_res))
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName.in_(uid_res))
        if m_args['betTimeLower'] is not None:
            criterin_bets.add(BlastBets.actionTime >= m_args['betTimeLower'])
            criterin_credit.add(BlastBetsCredit.betTime >= m_args['betTimeLower'])
            criterin_city.add(EntertainmentCityBetsDetail.BetTime >= m_args['betTimeLower'])
        if m_args['betTimeUpper'] is not None:
            criterin_bets.add(BlastBets.actionTime <= m_args['betTimeUpper'])
            criterin_credit.add(BlastBetsCredit.betTime <= m_args['betTimeUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.BetTime <= m_args['betTimeUpper'])
        if m_args['payoutTimeLower'] is not None:
            criterin_bets.add(BlastBets.kjTime >= m_args['payoutTimeLower'])
            criterin_credit.add(BlastBetsCredit.drawTime >= m_args['payoutTimeLower'])
            criterin_city.add(EntertainmentCityBetsDetail.ReckonTime >= m_args['payoutTimeLower'])
        if m_args['payoutTimeUpper'] is not None:
            criterin_bets.add(BlastBets.kjTime <= m_args['payoutTimeUpper'])
            criterin_credit.add(BlastBetsCredit.drawTime <= m_args['payoutTimeUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.ReckonTime <= m_args['payoutTimeUpper'])

        if m_args['betnumber'] is not None:
            criterin_bets.add(BlastBets.wjorderId == m_args['betnumber'])
            criterin_credit.add(BlastBetsCredit.orderId == m_args['betnumber'])
            criterin_city.add(EntertainmentCityBetsDetail.BillNo == m_args['betnumber'])
        if m_args['gameId'] is not None:
            criterin_bets.add(BlastBets.actionNo == m_args['gameId'])
            criterin_credit.add(BlastBetsCredit.gameIssue == m_args['gameId'])
            criterin_city.add(EntertainmentCityBetsDetail.GameCode == m_args['gameId'])
        if m_args['gameName'] is not None:
            res = db.session.query(BlastType.id).filter(BlastType.title == m_args['gameName']).first()
            if res is not None:
                res = res[0]
            criterin_bets.add(BlastBets.type == res)
            criterin_credit.add(BlastBetsCredit.gameType == res)
            criterin_city.add(EntertainmentCityBetsDetail.GameTypeInfo == m_args['gameName'])
        if m_args['gameNameLike'] is not None:
            res = db.session.query(BlastType.id).filter(BlastType.title .like('%' + m_args['gameNameLike']  + '%')).all()
            res_in = []
            if res is not None:
                for res_one in res:
                    res_in.append(res_one[0])
            else:
                res_in = []
            criterin_bets.add(BlastBets.type.in_(res_in))
            criterin_credit.add(BlastBetsCredit.gameType.in_(res_in))
            criterin_city.add(EntertainmentCityBetsDetail.GameTypeInfo.like('%' + m_args['gameNameLike']  + '%'))
        if m_args['status'] is not None:
            criterin_bets.add(BlastBets.state == m_args['status'])
            criterin_credit.add(BlastBetsCredit.state == m_args['status'])
            criterin_city.add(EntertainmentCityBetsDetail.Flag != m_args['status'])
        if m_args['betAmountLower'] is not None:
            criterin_bets.add((BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu) >= m_args['betAmountLower'])
            criterin_credit.add(BlastBetsCredit.betAmount >= m_args['betAmountLower'])
            criterin_city.add(EntertainmentCityBetsDetail.BetAmount >= m_args['betAmountLower'])
        if m_args['betAmountUpper'] is not None:
            criterin_bets.add((BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu) <= m_args['betAmountUpper'])
            criterin_credit.add(BlastBetsCredit.betAmount <= m_args['betAmountUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.BetAmount <= m_args['betAmountUpper'])
        if m_args['betAmountLowerYx'] is not None:
            criterin_bets.add(
                and_((BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu) >= m_args['betAmountLowerYx'],
                     BlastBets.state == 2))
            criterin_credit.add(
                and_(BlastBetsCredit.betAmount >= m_args['betAmountLowerYx'], BlastBetsCredit.state == 2))
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName >= m_args['betAmountLowerYx'])
        if m_args['betAmountUpperYx'] is not None:
            criterin_bets.add(
                and_((BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu) <= m_args['betAmountUpperYx'],
                     BlastBets.state == 2))
            criterin_credit.add(
                and_(BlastBetsCredit.betAmount <= m_args['betAmountUpperYx'], BlastBetsCredit.state == 2))
            criterin_city.add(EntertainmentCityBetsDetail.PlayerName <= m_args['betAmountUpperYx'])
        if m_args['payoutAmountLower'] is not None:
            criterin_bets.add(BlastBets.bonus >= m_args['payoutAmountLower'])
            criterin_credit.add(BlastBetsCredit.bonus >= m_args['payoutAmountLower'])
            criterin_city.add(EntertainmentCityBetsDetail.CusAccount >= m_args['payoutAmountLower'])
        if m_args['payoutAmountUpper'] is not None:
            criterin_bets.add(BlastBets.bonus <= m_args['payoutAmountUpper'])
            criterin_credit.add(BlastBetsCredit.bonus <= m_args['payoutAmountUpper'])
            criterin_city.add(EntertainmentCityBetsDetail.CusAccount <= m_args['payoutAmountUpper'])

        criterin = {}
        criterin['criterin_bets'] = criterin_bets
        criterin['criterin_credit'] = criterin_credit
        criterin['criterin_city'] = criterin_city
        return criterin

    def getKK(self, criterin):
        criterin_bets = criterin['criterin_bets']
        criterin_credit = criterin['criterin_credit']

        q5 = db.session.query(
            BlastBets.username.label('memberUsername'),
            literal('KK彩票').label('ECCode'),
            BlastType.title.label('playGame'),
            BlastBets.kjTime.label('payTime'),
            BlastBets.actionTime.label('betTime'),
            (BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu).label('betAmount'),
            BlastBets.bonus.label('paicai'),
        ).filter(*criterin_bets)
        q5 = q5.outerjoin(BlastType, BlastType.id == BlastBets.type)

        q6 = db.session.query(
            BlastBetsCredit.memberUsername.label('memberUsername'),
            literal('KK彩票').label('ECCode'),
            BlastType.title.label('playGame'),
            BlastBetsCredit.drawTime.label('payTime'),
            BlastBetsCredit.betTime.label('betTime'),
            BlastBetsCredit.betAmount.label('betAmount'),
            BlastBetsCredit.bonus.label('paicai'),
        ).filter(*criterin_credit)
        q6 = q6.outerjoin(BlastType, BlastType.id == BlastBetsCredit.gameType)

        res = union_all(q5, q6)
        user_alias_s = aliased(res, name='user_alias_s')
        betsprofitandloss = db.session.query(
            user_alias_s.c.memberUsername.label('memberUsername'),
            user_alias_s.c.playGame.label('playGame'),
            user_alias_s.c.ECCode.label('ECCode'),
            user_alias_s.c.payTime.label('payTime'),
            user_alias_s.c.betTime.label('betTime'),
            user_alias_s.c.betAmount.label('betAmount'),
            user_alias_s.c.betAmount.label('betAmountYX'),
            user_alias_s.c.paicai.label('paicai'),
        ).order_by(user_alias_s.c.payTime.desc()).all()

        return betsprofitandloss

    def getYlc(self, criterin):
        criterin_city = criterin['criterin_city']
        criterin_city.add(Dictionary.type == 900004)
        q7 = db.session.query(
            EntertainmentCityBetsDetail.PlayerName.label('memberUsername'),
            func.concat(EntertainmentCityBetsDetail.ECCode, '-', Dictionary.name).label('ECCode'),
            EntertainmentCityBetsDetail.GameTypeInfo.label('playGame'),
            EntertainmentCityBetsDetail.ReckonTime.label('payTime'),
            EntertainmentCityBetsDetail.BetTime.label('betTime'),
            EntertainmentCityBetsDetail.ValidBetAmount.label('betAmount'),
            EntertainmentCityBetsDetail.ValidBetAmount.label('YXbetAmount'),
            EntertainmentCityBetsDetail.CusAccount.label('paicai')
        ).filter(*criterin_city).order_by(EntertainmentCityBetsDetail.ReckonTime.desc())
        q7 = q7.outerjoin(Member, Member.username == EntertainmentCityBetsDetail.PlayerName)
        q7 = q7.outerjoin(Dictionary, Dictionary.code == EntertainmentCityBetsDetail.childType).all()

        return q7

    def getKKandYlc(self, criterin):
        criterin_bets = criterin['criterin_bets']
        criterin_credit = criterin['criterin_credit']
        criterin_city = criterin['criterin_city']
        criterin_city.add(Dictionary.type == 900004)

        q5 = db.session.query(
            BlastBets.username.label('memberUsername'),
            literal('KK彩票').label('ECCode'),
            BlastType.title.label('playGame'),
            BlastBets.kjTime.label('payTime'),
            BlastBets.actionTime.label('betTime'),
            (BlastBets.mode * BlastBets.actionNum * BlastBets.beiShu).label('betAmount'),
            BlastBets.bonus.label('paicai'),
        ).filter(*criterin_bets)
        q5 = q5.outerjoin(BlastType, BlastType.id == BlastBets.type)

        q6 = db.session.query(
            BlastBetsCredit.memberUsername.label('memberUsername'),
            literal('KK彩票').label('ECCode'),
            BlastType.title.label('playGame'),
            BlastBetsCredit.drawTime.label('payTime'),
            BlastBetsCredit.betTime.label('betTime'),
            BlastBetsCredit.betAmount.label('betAmount'),
            BlastBetsCredit.bonus.label('paicai'),
        ).filter(*criterin_credit)
        q6 = q6.outerjoin(BlastType, BlastType.id == BlastBetsCredit.gameType)



        q7 = db.session.query(
            EntertainmentCityBetsDetail.PlayerName.label('memberUsername'),
            func.concat(EntertainmentCityBetsDetail.ECCode, '-', Dictionary.name).label('ECCode'),
            EntertainmentCityBetsDetail.GameTypeInfo.label('playGame'),
            EntertainmentCityBetsDetail.ReckonTime.label('payTime'),
            EntertainmentCityBetsDetail.BetTime.label('betTime'),
            EntertainmentCityBetsDetail.ValidBetAmount.label('betAmount'),
            EntertainmentCityBetsDetail.CusAccount.label('paicai')
        ).filter(*criterin_city)
        q7 = q7.outerjoin(Member, Member.username == EntertainmentCityBetsDetail.PlayerName)
        q7 = q7.outerjoin(Dictionary, Dictionary.code == EntertainmentCityBetsDetail.childType)


        res = union_all(q5, q6, q7)
        user_alias_s = aliased(res, name='user_alias_s')
        betsprofitandloss = db.session.query(
            user_alias_s.c.memberUsername.label('memberUsername'),
            user_alias_s.c.ECCode.label('ECCode'),
            user_alias_s.c.playGame.label('playGame'),
            user_alias_s.c.payTime.label('payTime'),
            user_alias_s.c.betTime.label('betTime'),
            user_alias_s.c.betAmount.label('betAmount'),
            user_alias_s.c.betAmount.label('betAmountYX'),
            user_alias_s.c.paicai.label('paicai'),
        ).order_by(user_alias_s.c.payTime.desc()).all()

        return betsprofitandloss


'''
彩票管理
'''
class BlastTypeAPI(Resource):
    '''
    查询彩票
    '''
    @marshal_with(make_marshal_fields({
        'id': fields.Integer,
        'type': fields.Integer,
        'enable': fields.Integer,
        'sort': fields.Integer,
        'title': fields.String,
        'data_ftime': fields.Integer,
        'defaultViewGroup': fields.Integer,
        'num': fields.Integer,
        'group': fields.Integer,
    }))
    def get(self, id=None):
        criterion = set()
        m_args = type_parsers.parse_args(strict=True)
        if id:
            criterion.add(BlastType.id == id)        
        if m_args['typeList']:
            m_args['typeList'] = "[" + m_args['typeList']+"]"
            m_array = json.loads(m_args['typeList'])          
            criterion.add(BlastType.type.in_(m_array))
#         if m_args['groupList']:
#             m_array = json.loads(m_args['groupList'])          
#             criterion.add(BlastType.group.in_(m_array))
        if m_args['title']:
            criterion.add(BlastType.title.like('%'+m_args['title']+'%'))
        m_orm = BlastType()
        pagination = m_orm.getDataType(m_args['page'],m_args['pageSize'],criterion);
        return make_response_from_pagination(pagination)
    
    def put(self, id):
        args = type_parsers.parse_args(strict=True)
        del args['page'],args['pageSize'],args['groupList'],args['typeList']
        m_orm = BlastType()
        m_res = m_orm.update(id,**args)
        return {'success': True}, 201 


'''
彩票玩法大类管理
'''
class BlastPlayedGroupAPI(Resource):

    '''
    根据彩票type查询玩法大类
    '''
    @marshal_with(make_marshal_fields({
        'id': fields.Integer,
        'groupName': fields.String,
        'enable': fields.Integer,
        'type': fields.Integer,
        'android': fields.Integer,
        'sort': fields.Integer,
    }))
    def get(self, type,id=None):
        m_args = played_group_parsers.parse_args(strict=True)
        criterion = set()
        criterion.add(BlastPlayedGroup.type == type)
        if id:
            criterion.add(BlastPlayedGroup.id == id)
        m_orm = BlastPlayedGroup()
        pagination = m_orm.getPlayedByType(criterion,m_args['page'],m_args['pageSize'])
        return make_response_from_pagination(pagination)
        
    def put(self, type,id):
        m_args = played_group_parsers.parse_args(strict=True)
        del m_args['page'],m_args['pageSize']
        m_orm = BlastPlayedGroup()
        m_res = m_orm.update(id,m_args)
        return {'success': True}, 201     
        
'''
玩法赔率
'''
class BlastPlayedAPI(Resource):
    '''
    根据玩法大类得id询玩法设置
    '''
    @marshal_with(make_marshal_fields({
        'id': fields.Integer,
        'name': fields.String,
        'enable': fields.Integer,
        'type': fields.Integer,
        'bonusProp': fields.Float,
        'bonusPropBase': fields.Float,
        'groupId' : fields.Float,
        'android': fields.Integer,
        'sort': fields.Integer,
        'minCharge': fields.Integer,
        'allCount': fields.Integer,
        'maxCount': fields.Integer,
        'maxCharge': fields.Integer,
        'Rte': fields.Float,
        'rName': fields.String,
        'playid': fields.Integer,
        'remark': fields.String,
    }))
    def get(self, groupId,id = None):
        m_args = played_parser.parse_args(strict=True)
        criterion = set()
        pagination = None
        if id:
            criterion.add(BlastLHCRatio.playid == id)
            m_orm = BlastLHCRatio()
            pagination = m_orm.getData(criterion,m_args['page'],m_args['pageSize'])
        else:
            criterion.add(BlastPlayed.groupId == groupId)
            m_orm = BlastPlayed()
            pagination = m_orm.getPlayedByGroupId(criterion,m_args['page'],m_args['pageSize'])
        return make_response_from_pagination(pagination) 

    def put(self, groupId,id=None,lhid=None):
        #args = played_parser.parse_args(strict=True)
        #m_res = None
        #del args['page'],args['pageSize']
#         if lhid:
#             m_orm = BlastLHCRatio()
#             m_res = m_orm.update(lhid, args)
#         else:
#             m_orm = BlastPlayed()
#             m_res = m_orm.update(id,**args)
#         return {'success': True}, 201
        if id:
            m_args = request.get_json()
            m_orm = BlastLHCRatio()
            m_res = m_orm.update(playeid=id,**m_args)
        else:
            m_args = request.get_json()
            m_orm = BlastPlayed()
            m_res = m_orm.update(groupId,**m_args)
        return {'success': True}, 201


'''
彩票玩法大类管理--信用玩法
'''
class BlastPlayedGroupCreditAPI(Resource):
    '''
    根据彩票type查询玩法大类
    '''

    @marshal_with(make_marshal_fields({
        'id': fields.Integer,
        'groupName': fields.String,
        'enable': fields.Integer,
        'type': fields.Integer,
        'typename': fields.String,
        'sort': fields.Integer,
    }))
    def get(self, type, id=None):
        m_args = played_group_credit_parsers.parse_args(strict=True)
        criterion = set()
        criterion.add(BlastPlayedGroupCredit.type == type)
        if id:
            criterion.add(BlastPlayedGroupCredit.id == id)
        m_orm = BlastPlayedGroupCredit()
        pagination = m_orm.getPlayedByType(criterion, m_args['page'], m_args['pageSize'])
        return make_response_from_pagination(pagination)

    def put(self, type, id):
        m_args = played_group_credit_parsers.parse_args(strict=True)
        del m_args['page'], m_args['pageSize']
        m_orm = BlastPlayedGroupCredit()
        m_res = m_orm.update(id, m_args)
        return {'success': True}, 201


'''
信用玩法赔率
'''
class BlastPlayedCreditAPI(Resource):
    '''
    根据玩法大类得id询玩法设置
    '''
    @marshal_with(make_marshal_fields({
        'id': fields.Integer,
        'name': fields.String,
        'enable': fields.Integer,
        'type': fields.Integer,
        'bonusProp': fields.Float,
        'groupId' : fields.Float,
        'ruleName': fields.String,
        'remark': fields.String,
        'sort': fields.Integer,
        'minCharge': fields.Integer,
        'allCount': fields.Integer,
        'maxCount': fields.Integer,
        'maxCharge': fields.Integer,
    }))
    def get(self, groupId,id = None):
        m_args = played_credit_parser.parse_args(strict=True)
        criterion = set()
        pagination = None
        if id:
            criterion.add(BlastLHCRatio.playid == id)
            m_orm = BlastLHCRatio()
            pagination = m_orm.getData(criterion,m_args['page'],m_args['pageSize'])
        else:
            criterion.add(BlastPlayedCredit.groupId == groupId)
            m_orm = BlastPlayedCredit()
            pagination = m_orm.getPlayedByGroupId(criterion,m_args['page'],m_args['pageSize'])
        return make_response_from_pagination(pagination)

    def put(self, groupId, id=None,lhid=None):

        if id:
            m_args = request.get_json()
            m_orm = BlastPlayedCredit()
            m_res = m_orm.update(id, **m_args)
        else:
            m_args = request.get_json()
            m_orm = BlastPlayedCredit()
            m_res = m_orm.update(groupId, **m_args)
        return {'success': True}, 201

