from flask_restful import Resource
from app.models import db
from app.models.blast_bets import *
from sqlalchemy import func
from app.models.entertainment_city_bets_detail import *
from sqlalchemy.sql import union,union_all
from flask_restful.reqparse import RequestParser
from ..common import *
from sqlalchemy.orm import aliased
from app.models.common.utils import *
from app.api_0_1.common.utils import *
class FanshuiQuery(Resource):
    def get(self):
        ''''''
        parser = RequestParser(trim=True)
        parser.add_argument('page', type=int, default=DEFAULT_PAGE)
        parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
        parser.add_argument('timeLower', type=int)
        parser.add_argument('timeUpper', type=int)
        args = parser.parse_args(strict=True)

        result_BlastBets_set = set()
        result_BlastBets_set.add(BlastBets.state == 2)
        result_BlastBetsCredit_set = set()
        result_BlastBetsCredit_set.add(BlastBetsCredit.state == 2)
        result_EntertainmentCityBetsDetail_set = set()
        result_EntertainmentCityBetsDetail_set.add(EntertainmentCityBetsDetail.Flag == 1)

        if args['timeLower']:
            result_BlastBets_set.add(BlastBets.actionTime >= args['timeLower'])
            result_BlastBetsCredit_set.add(BlastBetsCredit.betTime >= args['timeLower'])
            result_EntertainmentCityBetsDetail_set.add(EntertainmentCityBetsDetail.BetTime >= args['timeLower'])
        if args['timeUpper']:
            result_BlastBets_set.add(BlastBets.actionTime <= args['timeUpper'] + SECONDS_PER_DAY)
            result_BlastBetsCredit_set.add(BlastBetsCredit.betTime <= args['timeUpper'] + SECONDS_PER_DAY)
            result_EntertainmentCityBetsDetail_set.add(EntertainmentCityBetsDetail.BetTime <= args['timeUpper'] + SECONDS_PER_DAY)



        '''查询blast_bet表'''
        result_BlastBets = db.session.query(
            BlastBets.username.label('username'),
            func.sum(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label('betAmount'),
            BlastBets.state.label('state')
        ).group_by(BlastBets.username).filter(*result_BlastBets_set).subquery()
        '''查询tb_bets_credit表'''
        result_BlastBetsCredit = db.session.query(
            BlastBetsCredit.memberUsername.label('username'),
            func.sum(BlastBetsCredit.betAmount).label('betAmount'),
            BlastBetsCredit.state.label('state')
        ).group_by(BlastBetsCredit.memberUsername).filter(*result_BlastBetsCredit_set).subquery()

        '''查询tb_entertainment_city_bets_detail表'''
        result_EntertainmentCityBetsDetail = db.session.query(
            EntertainmentCityBetsDetail.PlayerName.label('username'),
            EntertainmentCityBetsDetail.ECCode.label('ECCode'),
            EntertainmentCityBetsDetail.childType.label('childType'),
            func.sum(EntertainmentCityBetsDetail.BetAmount).label('betAmount'),
            EntertainmentCityBetsDetail.Flag.label('state'),

        ).group_by(
            EntertainmentCityBetsDetail.PlayerName,
            EntertainmentCityBetsDetail.ECCode,
            EntertainmentCityBetsDetail.childType,
        ).filter(*result_EntertainmentCityBetsDetail_set).all()



        '''blast_bet和tb_bets_credit组合查询'''
        result_BB_left_l = db.session.query(
            result_BlastBets.c.username.label('result_BlastBets_username'),
            result_BlastBets.c.betAmount.label('result_BlastBets_betAmount'),
            result_BlastBets.c.state.label('result_BlastBets_state'),
            result_BlastBetsCredit.c.username.label('result_BlastBetsCredit_username'),
            result_BlastBetsCredit.c.betAmount.label('result_BlastBetsCredit_betAmount'),
            result_BlastBetsCredit.c.state.label('result_BlastBetsCredit_state'),
        )
        result_BB_left_l = result_BB_left_l.outerjoin(result_BlastBetsCredit,result_BlastBetsCredit.c.username == result_BlastBets.c.username)

        result_BBC_right_l = db.session.query(
            result_BlastBets.c.username.label('result_BlastBets_username'),
            result_BlastBets.c.betAmount.label('result_BlastBets_betAmount'),
            result_BlastBets.c.state.label('result_BlastBets_state'),
            result_BlastBetsCredit.c.username.label('result_BlastBetsCredit_username'),
            result_BlastBetsCredit.c.betAmount.label('result_BlastBetsCredit_betAmount'),
            result_BlastBetsCredit.c.state.label('result_BlastBetsCredit_state')
        )
        result_BBC_right_l = result_BBC_right_l.outerjoin(result_BlastBets,result_BlastBets.c.username == result_BlastBetsCredit.c.username)

        result_all_1 = union(result_BB_left_l, result_BBC_right_l)
        # a = execute(result_all_1)
        # print(a)
        user_alias = aliased(result_all_1, name='user_alias')
        user_alias = db.session.query(user_alias).order_by().all()
        # print('***********************************************************************')
        # print(user_alias)
        # print('***********************************************************************')
        # print(result_EntertainmentCityBetsDetail)
        # print('***********************************************************************')






