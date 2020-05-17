from flask import request, g, current_app
from flask_restful import Resource, marshal_with, fields
from flask_restful.reqparse import RequestParser
from sqlalchemy.sql import union, union_all
from app.models import db
from app.models.common.utils import *
from app.models.member import MemberAccessLog
from ..common import *
from ..common.utils import *
import time, datetime
from datetime import timedelta
from app.models.member_account_change import MemberAccountChangeRecord, Withdrawal, Deposit
from sqlalchemy import func
from app.models.user import User
from app.models.member import Member
from app.models.blast_bets import BlastBets, BlastBetsCredit
from app.models.entertainment_city_bets_detail import EntertainmentCityBetsDetail
from sqlalchemy.orm import aliased
from app.models.report import Resports
from app.common.dataUtils import getData, changeData

import re,ast


class getAllBetsAmount(Resource):

	def get(self):
		now = int(time.time())
		last_ten_minutes = int(now - 60 * 10)
		last_three = int(now - 60 * 60 * 3)


		today = datetime.date.today()
		zeroPointToday = int(time.mktime(today.timetuple()))

		betsAccount_guan = db.session.query(
			BlastBets.username.label('username')).filter(
			BlastBets.actionTime >= last_ten_minutes, BlastBets.actionTime < now)
		betsAccount_xinyong = db.session.query(
			BlastBetsCredit.memberUsername.label('username')).filter(
			BlastBetsCredit.betTime >= last_ten_minutes, BlastBetsCredit.betTime < now)
		betsAccount_city = db.session.query(
			EntertainmentCityBetsDetail.PlayerName.label('username')).filter(
			EntertainmentCityBetsDetail.BetTime >= last_ten_minutes, EntertainmentCityBetsDetail.BetTime < now)
		result = union_all(betsAccount_guan, betsAccount_xinyong,betsAccount_city)
		user_alias = aliased(result, name='user_alias')
		betsAccount = db.session.query(user_alias.c.username).all()
		args = []
		for m_arg in betsAccount:
			args.append(m_arg[0])
		members = db.session.query(func.count(Member.id)).filter(Member.type == 0, Member.isTsetPLay == 0,
																 Member.username.in_(args)).all()[0][0]
		betSum = {}
		betSum['number'] = members
		betSum['now'] = now
		betSum['last_ten_minutes'] = last_ten_minutes
		betSum['last_three'] = last_three
		betSum['zero'] = zeroPointToday
		return make_response(betSum)


# 統計資料
class Reports(Resource):

	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('timeLower', type=int)
		parser.add_argument('timeUpper', type=int)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('memberType', type=int)
		parser.add_argument('gameType', type=str)
		parser.add_argument('gameName', type=str)
		args = parser.parse_args(strict=True)
		if args['gameType'] is None or not args['gameType']:
			return make_response([])
		if args['gameName'] is None or not args['gameName']:
			return make_response([])
		if args['gameType']:
			args['gameType'] = ast.literal_eval(args['gameType'])
		else:
			args['gameType'] = []
		if args['gameName']:

		else:
			args['gameName'] = []
		if args['memberUsername'] and args['memberType'] is not None:
			arg = []
			if args['memberType'] == 1:
				arg = [1, 9, 10, 11]
			elif args['memberType'] == 0:
				arg = [0]
			member = db.session.query(Member.id).filter(Member.username == args['memberUsername'],
														Member.type.in_(arg)).first()
			if member is None:
				if args['memberType'] == 0:
					return {
						'errorMsg': "该会员不存在",
						'success': False
					}
				if args['memberType'] == 1:
					return {
						'errorMsg': "该代理不存在",
						'success': False
					}
		if args['memberType'] == 1:
			if not args['memberUsername']:
				return {
					'errorMsg': "代理不能为空",
					'success': False
				}
		if args['memberType'] == 0:
			if not args['memberUsername']:
				return {
					'errorMsg': "会员不能为空",
					'success': False
				}
			member_parentId = db.session.query(Member.parent).filter(Member.username == args['memberUsername']).first()
			member_username = db.session.query(Member.username, Member.type).filter(
				Member.id == member_parentId[0]).first()
			res = {
				'username': member_username[0],
				'type': member_username[1],
				'uid': member_parentId[0],
				'ishave': 1
			}
			return make_response(data=[res])

		criterion_ylc = set()
		criterion_ylc_b = set()
		criterion_ylc_c = set()
		criterion_1 = set()
		criterion_2 = set()
		criterion_3 = set()
		criterion_4 = set()
		criterion_1.add(BlastBets.state == 2)
		criterion_2.add(BlastBetsCredit.state == 2)
		criterion_3.add(BlastBets.state == 2)
		criterion_4.add(BlastBetsCredit.state == 2)
		if args['timeLower']:
			criterion_ylc_c.add(EntertainmentCityBetsDetail.ReckonTime >= args['timeLower'])
			criterion_1.add(BlastBets.kjTime >= args['timeLower'])
			criterion_2.add(BlastBetsCredit.drawTime >= args['timeLower'])
			criterion_3.add(BlastBets.kjTime >= args['timeLower'])
			criterion_4.add(BlastBetsCredit.drawTime >= args['timeLower'])
		if args['timeUpper']:
			criterion_ylc_c.add(EntertainmentCityBetsDetail.ReckonTime <= args['timeUpper'])
			criterion_1.add(BlastBets.kjTime <= args['timeUpper'])
			criterion_2.add(BlastBetsCredit.drawTime <= args['timeUpper'])
			criterion_3.add(BlastBets.kjTime <= args['timeUpper'])
			criterion_4.add(BlastBetsCredit.drawTime <= args['timeUpper'])
		if args['memberUsername']:
			member = db.session.query(Member.id).filter(Member.username == args['memberUsername']).first()
			mId = member[0]
			q4 = db.session.query(Member.id).filter(func.find_in_set('{}'.format(mId), Member.parents),
													Member.type == 0, Member.isTsetPLay == 0)
			q_name = db.session.query(Member.username).filter(func.find_in_set('{}'.format(mId), Member.parents),
															  Member.isTsetPLay == 0, Member.type == 0)
		else:
			q4 = db.session.query(Member.id).filter(Member.type == 0, Member.isTsetPLay == 0)
			q_name = db.session.query(Member.username).filter(Member.isTsetPLay == 0, Member.type == 0)
		if "kk" in args['gameName']:
			criterion_1.add(BlastBets.uid.in_(q4))
			criterion_2.add(BlastBetsCredit.memberId.in_(q4))
			q5 = db.session.query(
				func.count(BlastBets.uid).label('uid'),
				func.sum(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label('amount')
			).filter(*criterion_1)
			q6 = db.session.query(
				func.count(BlastBetsCredit.memberId).label('uid'),
				func.sum(BlastBetsCredit.betAmount).label('amount')
			).filter(*criterion_2)
			q7 = union_all(q5, q6)
			kk_alias = aliased(q7, name='kk_alias')
			aa = db.session.query(
				func.sum(kk_alias.c.uid).label('uid'),
				func.sum(kk_alias.c.amount).label('amount')
			)
			q5_member = db.session.query(
				BlastBets.uid.label('memberId')
			).filter(*criterion_1)
			q6_member = db.session.query(
				BlastBetsCredit.memberId.label('memberId')
			).filter(*criterion_2)
			q5_q6_member = union_all(q5_member, q6_member)
			q5_q6 = aliased(q5_q6_member, name='mem_alias')
			q5_q6_mem = db.session.query(
				q5_q6.c.memberId.distinct().label('memberId')
			)

		if args['gameType'] is not None and 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in args[
			'gameName']:
			a = db.session.query(
				EntertainmentCityBetsDetail.id.label('uid'),
				EntertainmentCityBetsDetail.PlayerName.label('PlayerName'),
				EntertainmentCityBetsDetail.ValidBetAmount.label('BetAmount'),
				func.concat(EntertainmentCityBetsDetail.ECCode, '-', EntertainmentCityBetsDetail.childType).label(
					'gameType')
			).filter(*criterion_ylc_c).subquery()
			criterion_ylc.add(a.c.PlayerName.in_(q_name))
			if args['gameType']:
				criterion_ylc.add(a.c.gameType.in_(args['gameType']))
			bb = db.session.query(
				func.count(a.c.uid).label('uid'),
				func.sum(a.c.BetAmount).label('BetAmount')
			).filter(*criterion_ylc)

			aa_sum = db.session.query(
				a.c.PlayerName.label('PlayerName')
			).filter(*criterion_ylc)
			criterion_ylc_member = set()
			criterion_ylc_member.add(Member.username.in_(aa_sum))
			member_sum = db.session.query(func.count(Member.id)).filter(*criterion_ylc_member)

			if "kk" not in args['gameName']:
				betsAccount = bb.all()
				if betsAccount[0][1] is None:
					amount = 0
				else:
					amount = float(betsAccount[0][1])
				countUid = int(betsAccount[0][0])
				memberSum = member_sum.all()
				members = memberSum[0][0]

			else:
				Num = db.session.query(
					Member.id.label('memberId')
				).filter(*criterion_ylc_member)
				kk_num = union_all(q5_q6_mem, Num)
				kk_num_alias = aliased(kk_num, name='kk_num_alias')
				memberSum = db.session.query(
					func.count(kk_num_alias.c.memberId.distinct())
				).all()
				members = memberSum[0][0]

				q_ylc = union_all(aa, bb)
				user_alias = aliased(q_ylc, name='user_alias')
				betsAccount = db.session.query(
					func.sum(user_alias.c.uid),
					func.sum(user_alias.c.amount),
				).all()
				countUid = int(betsAccount[0][0])
				if betsAccount[0][1] is None:
					amount = 0
				else:
					amount = float(betsAccount[0][1])

		else:
			betsAccount = aa.all()
			countUid = int(betsAccount[0][0])
			if betsAccount[0][1] is None:
				amount = 0
			else:
				amount = float(betsAccount[0][1])
			q5_q6_mem = q5_q6_mem.subquery()
			members = db.session.query(
				func.count(q5_q6_mem.c.memberId)
			).first()[0]

		if "kk" in args['gameName']:
			criterion_3.add(BlastBets.uid.in_(q4))
			criterion_4.add(BlastBetsCredit.memberId.in_(q4))
			q9 = db.session.query(
				func.sum(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum - BlastBets.bonus).label('bonus'),
				func.sum(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label('betamount'),
			).filter(*criterion_3)
			q10 = db.session.query(
				func.sum(BlastBetsCredit.betAmount - BlastBetsCredit.bonus).label('bonus'),
				func.sum(BlastBetsCredit.betAmount).label('betamount'),
			).filter(*criterion_4)
			q11 = union_all(q9, q10)
			kk_s_alias = aliased(q11, name='kk_s_alias')
			bb = db.session.query(
				func.sum(kk_s_alias.c.bonus).label('bonus'),
				func.sum(kk_s_alias.c.betamount).label('betamount')
			)

		if args['gameType'] is not None and 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in args[
			'gameName']:
			b = db.session.query(
				EntertainmentCityBetsDetail.id.label('uid'),
				EntertainmentCityBetsDetail.PlayerName.label('PlayerName'),
				EntertainmentCityBetsDetail.ValidBetAmount.label('BetAmount'),
				(EntertainmentCityBetsDetail.ValidBetAmount - EntertainmentCityBetsDetail.CusAccount).label(
					'CusAccount'),
				func.concat(EntertainmentCityBetsDetail.ECCode, '-', EntertainmentCityBetsDetail.childType).label(
					'gameType')
			).filter(*criterion_ylc_c).subquery()
			criterion_ylc_b.add(b.c.PlayerName.in_(q_name))
			if args['gameType']:
				criterion_ylc_b.add(b.c.gameType.in_(args['gameType']))
			res_b = db.session.query(
				func.sum(b.c.CusAccount).label('bonus'),
				func.sum(b.c.BetAmount).label('betamount')
			).filter(*criterion_ylc_b)
			if "kk" not in args['gameName']:
				yx_sy = res_b.all()
				if yx_sy[0][0] is None:
					bonus = 0
				else:
					bonus = float(yx_sy[0][0])
				if yx_sy[0][1] is None:
					betamount = 0
				else:
					betamount = float(yx_sy[0][1])
			else:
				q_ylc_b = union_all(bb, res_b)
				user_s_alias = aliased(q_ylc_b, name='user_s_alias')
				yx_sy = db.session.query(
					func.sum(user_s_alias.c.bonus),
					func.sum(user_s_alias.c.betamount),
				).all()
				if yx_sy[0][0] is None:
					bonus = 0
				else:
					bonus = float(yx_sy[0][0])
				if yx_sy[0][1] is None:
					betamount = 0
				else:
					betamount = float(yx_sy[0][1])

		else:
			yx_sy = bb.all()
			if yx_sy[0][0] is None:
				bonus = 0
			else:
				bonus = float(yx_sy[0][0])
			if yx_sy[0][1] is None:
				betamount = 0
			else:
				betamount = float(yx_sy[0][1])


		if args['memberUsername']:
			mem_parent = db.session.query(Member.parent,Member.id,Member.type).filter(Member.username == args['memberUsername']).first()
			tjzl_dict = {}
			tjzl_dict['members'] = members
			tjzl_dict['countUid'] = countUid
			tjzl_dict['amount'] = amount
			tjzl_dict['bonus'] = bonus
			tjzl_dict['betamount'] = betamount
			tjzl_dict['uid'] = mem_parent[1]
			tjzl_dict['username'] = args['memberUsername']
			tjzl_dict['type'] = mem_parent[2]
			if mem_parent[0]:
				mem_info = db.session.query(Member.username, Member.type).filter(Member.id == mem_parent[0]).first()
				tjzl_dict['parent_ID'] = mem_parent[0]
				tjzl_dict['parent_name'] = mem_info[0]
				tjzl_dict['parent_type'] = mem_info[1]
			else:
				if args['memberType'] is None:
					tjzl_dict['uid'] = None
					tjzl_dict['username'] = None
					tjzl_dict['type'] = None
				tjzl_dict['parent_ID'] = None
				tjzl_dict['parent_name'] = None
				tjzl_dict['parent_type'] = None
		else:
			tjzl_dict = {}
			tjzl_dict['members'] = members
			tjzl_dict['countUid'] = countUid
			tjzl_dict['amount'] = amount
			tjzl_dict['bonus'] = bonus
			tjzl_dict['betamount'] = betamount
			if args['memberType'] is None:
				tjzl_dict['uid'] = None
				tjzl_dict['username'] = None
				tjzl_dict['type'] = None
			tjzl_dict['parent_ID'] = None
			tjzl_dict['parent_name'] = None
			tjzl_dict['parent_type'] = None
		result = [tjzl_dict]
		return make_response(result)


# 詳細資料
class StatisticalReport(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('timeLower', type=int)
		parser.add_argument('timeUpper', type=int)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('memberType', type=int)
		parser.add_argument('gameType', type=str)
		parser.add_argument('gameName', type=str)
		args = parser.parse_args(strict=True)
		if args['gameType'] is None:
			return make_response([])
		if args['gameName'] is None:
			return make_response([])
		if args['gameType']:
			args['gameType'] = ast.literal_eval(args['gameType'])
		else:
			args['gameType'] = []
		if args['gameName']:
			args['gameName'] = ast.literal_eval(args['gameName'])
		else:
			args['gameName'] = []
		if args['memberType'] == 0:
			if not args['memberUsername']:
				return {
					'errorMsg': "会员不能为空",
					'success': False
				}
		if args['memberType'] == 1:
			if not args['memberUsername']:
				return {
					'errorMsg': "代理不能为空",
					'success': False
				}

		# 驗證代理或者會員是否存在
		if args['memberUsername'] and args['memberType'] is not None:
			arg = []
			if args['memberType'] == 1:
				arg = [1, 9, 10, 11]
			elif args['memberType'] == 0:
				arg = [0]
			member = db.session.query(Member.id).filter(Member.username == args['memberUsername'],
														Member.type.in_(arg)).first()
			if member is None:
				if args['memberType'] == 0:
					return {
						'errorMsg': "该会员不存在",
						'success': False
					}
				if args['memberType'] == 1:
					return {
						'errorMsg': "该代理不存在",
						'success': False
					}

		# 選中會員，輸入會員名稱
		if args['memberUsername'] and args['memberType'] == 0:
			member_id = db.session.query(Member.id).filter(Member.username == args['memberUsername'], Member.type == 0,
														   Member.isTsetPLay == 0).first()
			if member_id is None:
				return {
					'errorMsg': "该会员不存在",
					'success': False
				}
			mId = member_id[0]

			criterion_ylc = set()
			criterion_ylc_yxsy = set()
			criterion_ylc_a = set()
			criterion_1 = set()
			criterion_2 = set()
			criterion_3 = set()
			criterion_4 = set()
			criterion_1.add(BlastBets.state == 2)
			criterion_2.add(BlastBetsCredit.state == 2)
			criterion_3.add(BlastBets.state == 2)
			criterion_4.add(BlastBetsCredit.state == 2)
			if args['timeLower']:
				criterion_1.add(BlastBets.kjTime >= args['timeLower'])
				criterion_2.add(BlastBetsCredit.drawTime >= args['timeLower'])
				criterion_ylc_a.add(EntertainmentCityBetsDetail.ReckonTime >= args['timeLower'])
				criterion_3.add(BlastBets.kjTime >= args['timeLower'])
				criterion_4.add(BlastBetsCredit.drawTime >= args['timeLower'])
			if args['timeUpper']:
				criterion_1.add(BlastBets.kjTime <= args['timeUpper'])
				criterion_2.add(BlastBetsCredit.drawTime <= args['timeUpper'])
				criterion_ylc_a.add(EntertainmentCityBetsDetail.ReckonTime <= args['timeUpper'])
				criterion_3.add(BlastBets.kjTime <= args['timeUpper'])
				criterion_4.add(BlastBetsCredit.drawTime <= args['timeUpper'])
			# 單量和投注額
			if 'kk' in args['gameName']:
				criterion_1.add(BlastBets.uid == mId)
				q5 = db.session.query(
					BlastBets.uid.label('uid'),
					(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label('amount')
				).filter(*criterion_1)
				criterion_2.add(BlastBetsCredit.memberId == mId)
				q6 = db.session.query(
					BlastBetsCredit.memberId.label('uid'),
					BlastBetsCredit.betAmount.label('amount')
				).filter(*criterion_2)
				q7 = union_all(q5, q6)
				result = aliased(q7, name='user_alias')
				mem = db.session.query(
					result.c.uid.label('uid'),
					result.c.amount.label('amount')
				)

			if args['gameType'] is not None and 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in \
					args['gameName']:
				criterion_ylc_a.add(EntertainmentCityBetsDetail.PlayerName == args['memberUsername'])
				a = db.session.query(
					Member.id.label('uid'),
					EntertainmentCityBetsDetail.ValidBetAmount.label('BetAmount'),
					func.concat(EntertainmentCityBetsDetail.ECCode, '-', EntertainmentCityBetsDetail.childType).label(
						'gameType')
				).filter(*criterion_ylc_a)
				a = a.join(Member, Member.username == EntertainmentCityBetsDetail.PlayerName).subquery()
				if args['gameType']:
					criterion_ylc.add(a.c.gameType.in_(args['gameType']))
				res = db.session.query(
					a.c.uid.label('uid'),
					a.c.BetAmount.label('amount')
				).filter(*criterion_ylc)
				if "kk" not in args['gameName']:
					res = res.subquery()
					xx_member = db.session.query(
						res.c.uid.label('uid'),
						func.count(res.c.uid).label('countUid'),
						func.sum(res.c.amount).label('amount')
					).group_by(res.c.uid).subquery()
				else:
					q_ylc = union_all(mem, res)
					xx_mem_alias = aliased(q_ylc, name='xx_mem_alias')
					xx_member = db.session.query(
						xx_mem_alias.c.uid.label('uid'),
						func.count(xx_mem_alias.c.uid).label('countUid'),
						func.sum(xx_mem_alias.c.amount).label('amount')
					).group_by(xx_mem_alias.c.uid).subquery()
			else:
				mem = mem.subquery()
				xx_member = db.session.query(
					mem.c.uid.label('uid'),
					func.count(mem.c.uid).label('countUid'),
					func.sum(mem.c.amount).label('amount')
				).group_by(mem.c.uid).subquery()

			# 有效和損益
			if 'kk' in args['gameName']:
				criterion_3.add(BlastBets.uid == mId)
				criterion_4.add(BlastBetsCredit.memberId == mId)
				q_bets = db.session.query(
					BlastBets.uid.label('uid'),
					(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum - BlastBets.bonus).label('bonus'),
					(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label('betamount'),
				).filter(*criterion_3)
				q_credit = db.session.query(
					BlastBetsCredit.memberId.label('uid'),
					func.sum(BlastBetsCredit.betAmount - BlastBetsCredit.bonus).label('bonus'),
					func.sum(BlastBetsCredit.betAmount).label('betamount'),
				).filter(*criterion_4)
				q_bets_credit = union_all(q_bets, q_credit)
				bets_credit_alias = aliased(q_bets_credit, name='bets_credit_alias')
				aa = db.session.query(
					bets_credit_alias.c.uid.label('uid'),
					bets_credit_alias.c.bonus.label('bonus'),
					bets_credit_alias.c.betamount.label('betamount')
				)

			if args['gameType'] is not None and 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in \
					args['gameName']:
				b = db.session.query(
					Member.id.label('uid'),
					EntertainmentCityBetsDetail.ValidBetAmount.label('BetAmount'),
					(EntertainmentCityBetsDetail.ValidBetAmount - EntertainmentCityBetsDetail.CusAccount).label(
						'CusAccount'),
					func.concat(EntertainmentCityBetsDetail.ECCode, '-', EntertainmentCityBetsDetail.childType).label(
						'gameType')
				).filter(*criterion_ylc_a)
				b = b.join(Member, Member.username == EntertainmentCityBetsDetail.PlayerName).subquery()
				if args['gameType']:
					criterion_ylc_yxsy.add(b.c.gameType.in_(args['gameType']))
				res_yxsy = db.session.query(
					b.c.uid.label('uid'),
					b.c.CusAccount.label('bonus'),
					b.c.BetAmount.label('betamount')
				).filter(*criterion_ylc_yxsy)
				if "kk" not in args['gameName']:
					res_yxsy = res_yxsy.subquery()
					xx_yxsy = db.session.query(
						res_yxsy.c.uid.label('uid'),
						func.sum(res_yxsy.c.bonus).label('bonus'),
						func.sum(res_yxsy.c.betamount).label('betamount')
					).group_by(res_yxsy.c.uid).subquery()
				else:
					q_KK_ylc = union_all(aa, res_yxsy)
					KK_ylc_alias = aliased(q_KK_ylc, name='KK_ylc_alias')
					xx_yxsy = db.session.query(
						KK_ylc_alias.c.uid.label('uid'),
						func.sum(KK_ylc_alias.c.bonus).label('bonus'),
						func.sum(KK_ylc_alias.c.betamount).label('betamount'),
					).group_by(KK_ylc_alias.c.uid).subquery()
			else:
				aa = aa.subquery()
				xx_yxsy = db.session.query(
					aa.c.uid.label('uid'),
					func.sum(aa.c.bonus).label('bonus'),
					func.sum(aa.c.betamount).label('betamount')
				).group_by(aa.c.uid).subquery()

			xxzl_member = db.session.query(
				Member.username,
				Member.type,
				xx_yxsy.c.uid,
				xx_yxsy.c.bonus,
				xx_yxsy.c.betamount,
				xx_member.c.countUid,
				xx_member.c.amount
			)
			xxzl_member = xxzl_member.join(xx_member, xx_yxsy.c.uid == xx_member.c.uid)
			xxzl_member = xxzl_member.join(Member, xx_yxsy.c.uid == Member.id)
			xxzl_member = xxzl_member.all()

			xx_res = []
			Parent = db.session.query(Member.parent).filter(Member.id == mId).first()[0]
			Parent_info = db.session.query(Member.username, Member.type).filter(Member.id == Parent).first()
			for x in xxzl_member:
				xx_res.append(
					{
						'username': x.username,
						'type': x.type,
						'uid': x.uid,
						'bonus': float(x.bonus),
						'betamount': float(x.betamount),
						'countUid': x.countUid,
						'amount': float(x.amount),
						'parent_ID': Parent,
						'parent_name': Parent_info[0],
						'parent_type': Parent_info[1],
					}
				)
			xxzl_member_dict = {}
			xxzl_member_dict['agensList'] = []
			xxzl_member_dict['memberList'] = xx_res
			xxzl_member_dict['parent_ID'] = Parent
			xxzl_member_dict['parent_name'] = Parent_info[0]
			xxzl_member_dict['parent_type'] = Parent_info[1]
			result = [xxzl_member_dict]
			return make_response(result)

		# 篩選出代理下的直系會員
		if args['memberUsername'] and args['memberType'] == 1 or not args['memberType']:
			criterion_ylc = set()
			criterion_ylc_yxsy = set()
			criterion_ylc_a = set()
			criterion_1 = set()
			criterion_2 = set()
			criterion_3 = set()
			criterion_4 = set()
			criterion_1.add(BlastBets.state == 2)
			criterion_2.add(BlastBetsCredit.state == 2)
			criterion_3.add(BlastBets.state == 2)
			criterion_4.add(BlastBetsCredit.state == 2)
			if args['timeLower']:
				criterion_1.add(BlastBets.kjTime >= args['timeLower'])
				criterion_2.add(BlastBetsCredit.drawTime >= args['timeLower'])
				criterion_ylc_a.add(EntertainmentCityBetsDetail.ReckonTime >= args['timeLower'])
				criterion_3.add(BlastBets.kjTime >= args['timeLower'])
				criterion_4.add(BlastBetsCredit.drawTime >= args['timeLower'])
			if args['timeUpper']:
				criterion_1.add(BlastBets.kjTime <= args['timeUpper'])
				criterion_2.add(BlastBetsCredit.drawTime <= args['timeUpper'])
				criterion_ylc_a.add(EntertainmentCityBetsDetail.ReckonTime <= args['timeUpper'])
				criterion_3.add(BlastBets.kjTime <= args['timeUpper'])
				criterion_4.add(BlastBetsCredit.drawTime <= args['timeUpper'])
			if not args['memberType']:
				q1 = db.session.query(
					Member.id,
				).filter(Member.parent.is_(None), Member.type == 0, Member.isTsetPLay == 0)
				q2 = db.session.query(
					Member.username,
				).filter(Member.parent.is_(None), Member.type == 0, Member.isTsetPLay == 0)
			else:
				member = db.session.query(Member.id).filter(Member.username == args['memberUsername']).first()
				if member is None:
					return {
						'errorMsg': "该会员不存在",
						'success': False
					}
				mId = member[0]
				q1 = db.session.query(
					Member.id,
				).filter(Member.parent == mId, Member.type == 0, Member.isTsetPLay == 0)
				q2 = db.session.query(
					Member.username,
				).filter(Member.parent == mId, Member.type == 0, Member.isTsetPLay == 0)

			# 單量和投注額
			if 'kk' in args['gameName']:
				criterion_1.add(BlastBets.uid.in_(q1))
				criterion_2.add(BlastBetsCredit.memberId.in_(q1))
				q31 = db.session.query(
					BlastBets.uid.label('uid'),
					(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label('amount')
				).filter(*criterion_1)
				q32 = db.session.query(
					BlastBetsCredit.memberId.label('uid'),
					BlastBetsCredit.betAmount.label('amount')
				).filter(*criterion_2)
				q33 = union_all(q31, q32)
				daili_mem_alias = aliased(q33, name='daili_mem_alias')
				daili_mem = db.session.query(
					daili_mem_alias.c.uid.label('uid'),
					daili_mem_alias.c.amount.label('amount')
				)

			if args['gameType'] is not None and 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in \
					args['gameName']:
				criterion_ylc_a.add(EntertainmentCityBetsDetail.PlayerName.in_(q2))
				a = db.session.query(
					Member.id.label('uid'),
					EntertainmentCityBetsDetail.ValidBetAmount.label('BetAmount'),
					func.concat(EntertainmentCityBetsDetail.ECCode, '-', EntertainmentCityBetsDetail.childType).label(
						'gameType')
				).filter(*criterion_ylc_a)
				a = a.join(Member, Member.username == EntertainmentCityBetsDetail.PlayerName).subquery()
				if args['gameType']:
					criterion_ylc.add(a.c.gameType.in_(args['gameType']))
				res = db.session.query(
					a.c.uid.label('uid'),
					a.c.BetAmount.label('amount')
				).filter(*criterion_ylc)
				if "kk" not in args['gameName']:
					res = res.subquery()
					xx_member = db.session.query(
						res.c.uid.label('uid'),
						func.count(res.c.uid).label('countUid'),
						func.sum(res.c.amount).label('amount')
					).group_by(res.c.uid).subquery()
				else:
					q_ylc = union_all(daili_mem, res)
					xx_mem_alias = aliased(q_ylc, name='xx_mem_alias')
					xx_member = db.session.query(
						xx_mem_alias.c.uid.label('uid'),
						func.count(xx_mem_alias.c.uid).label('countUid'),
						func.sum(xx_mem_alias.c.amount).label('amount')
					).group_by(xx_mem_alias.c.uid).subquery()
			else:
				daili_mem = daili_mem.subquery()
				xx_member = db.session.query(
					daili_mem.c.uid.label('uid'),
					func.count(daili_mem.c.uid).label('countUid'),
					func.sum(daili_mem.c.amount).label('amount')
				).group_by(daili_mem.c.uid).subquery()

			# 有效和損益
			if 'kk' in args['gameName']:
				criterion_3.add(BlastBets.uid.in_(q1))
				criterion_4.add(BlastBetsCredit.memberId.in_(q1))
				q_bets = db.session.query(
					BlastBets.uid.label('uid'),
					(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum - BlastBets.bonus).label(
						'bonus'),
					(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label('betamount'),
				).filter(*criterion_3)
				q_credit = db.session.query(
					BlastBetsCredit.memberId.label('uid'),
					(BlastBetsCredit.betAmount - BlastBetsCredit.bonus).label('bonus'),
					(BlastBetsCredit.betAmount).label('betamount'),
				).filter(*criterion_4)
				q_bets_credit = union_all(q_bets, q_credit)
				bets_credit_alias = aliased(q_bets_credit, name='bets_credit_alias')
				aa = db.session.query(
					bets_credit_alias.c.uid.label('uid'),
					bets_credit_alias.c.bonus.label('bonus'),
					bets_credit_alias.c.betamount.label('betamount')
				)

			if args['gameType'] is not None and 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in \
					args['gameName']:
				b = db.session.query(
					Member.id.label('uid'),
					EntertainmentCityBetsDetail.ValidBetAmount.label('BetAmount'),
					(EntertainmentCityBetsDetail.ValidBetAmount - EntertainmentCityBetsDetail.CusAccount).label(
						'CusAccount'),
					func.concat(EntertainmentCityBetsDetail.ECCode, '-',
								EntertainmentCityBetsDetail.childType).label(
						'gameType')
				).filter(*criterion_ylc_a)
				b = b.join(Member, Member.username == EntertainmentCityBetsDetail.PlayerName).subquery()
				if args['gameType']:
					criterion_ylc_yxsy.add(b.c.gameType.in_(args['gameType']))
				res_yxsy = db.session.query(
					b.c.uid.label('uid'),
					b.c.CusAccount.label('bonus'),
					b.c.BetAmount.label('betamount')
				).filter(*criterion_ylc_yxsy)
				if "kk" not in args['gameName']:
					res_yxsy = res_yxsy.subquery()
					xx_yxsy = db.session.query(
						res_yxsy.c.uid.label('uid'),
						func.sum(res_yxsy.c.bonus).label('bonus'),
						func.sum(res_yxsy.c.betamount).label('betamount')
					).group_by(res_yxsy.c.uid).subquery()
				else:
					q_KK_ylc = union_all(aa, res_yxsy)
					KK_ylc_alias = aliased(q_KK_ylc, name='KK_ylc_alias')
					xx_yxsy = db.session.query(
						KK_ylc_alias.c.uid.label('uid'),
						func.sum(KK_ylc_alias.c.bonus).label('bonus'),
						func.sum(KK_ylc_alias.c.betamount).label('betamount'),
					).group_by(KK_ylc_alias.c.uid).subquery()
			else:
				aa = aa.subquery()
				xx_yxsy = db.session.query(
					aa.c.uid.label('uid'),
					func.sum(aa.c.bonus).label('bonus'),
					func.sum(aa.c.betamount).label('betamount')
				).group_by(aa.c.uid).subquery()

			xxzl = db.session.query(
				Member.username,
				Member.type,
				xx_yxsy.c.uid,
				xx_yxsy.c.bonus,
				xx_yxsy.c.betamount,
				xx_member.c.countUid,
				xx_member.c.amount
			)
			xxzl = xxzl.join(xx_member, xx_yxsy.c.uid == xx_member.c.uid)
			xxzl = xxzl.join(Member, xx_yxsy.c.uid == Member.id)
			xxzl = xxzl.all()

			xx_res = []
			for x in xxzl:
				xx_res.append(
					{
						'username': x.username,
						'type': x.type,
						'uid': x.uid,
						'bonus': float(x.bonus),
						'betamount': float(x.betamount),
						'countUid': x.countUid,
						'amount': float(x.amount)
					}
				)

		'''
			代理
		'''
		m_sql_s = '''
				SELECT
				uid,
				username,
				type,
				'''
		if not args['memberType']:
			m_sql_e = '''
					from (SELECT uid,username,type from blast_members where parentId is NULL and type != 0) aa
					'''
		else:
			m_sql_e = '''
						from (SELECT uid,username,type from blast_members where parentId = {} and type != 0) aa
						'''.format(member[0])

		TimeLower = -2208981211
		TimeUpper = 32503687932
		# 只有kk
		if 'kk' in args['gameName'] and 'AG' not in args['gameName'] and 'PT' not in args[
			'gameName'] and 'KAIYUAN' not in args['gameName']:
			if args['timeLower'] and not args['timeUpper']:
				timeLower = args['timeLower']
				kjTime = 'kjTime >=' + str(timeLower) + ' and'
				drawTime = 'drawTime >=' + str(timeLower) + ' and'
			if not args['timeLower'] and args['timeUpper']:
				timeUpper = args['timeUpper']
				kjTime = 'kjTime <=' + str(timeUpper) + ' and'
				drawTime = 'drawTime <=' + str(timeUpper) + ' and'
			if args['timeLower'] and args['timeUpper']:
				timeLower = args['timeLower']
				timeUpper = args['timeUpper']
				kjTime = 'kjTime >=' + str(timeLower) + ' and kjTime <=' + str(timeUpper) + ' and'
				drawTime = 'drawTime >=' + str(timeLower) + ' and drawTime <=' + str(timeUpper) + ' and'
			if not args['timeLower'] and not args['timeUpper']:
				kjTime = 'kjTime >=' + str(TimeLower) + ' and kjTime <=' + str(TimeUpper) + ' and'
				drawTime = 'drawTime >=' + str(TimeLower) + ' and drawTime <=' + str(TimeUpper) + ' and'

			m_str_member = '''					
						(SELECT count(uid) FROM blast_members where type = 0 and isTsetPLay = 0 
						and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)) 
						and username in (SELECT memberUsername as username from tb_bets_credit where {drawTime} state = 2 
						UNION all SELECT username as username from blast_bets where {kjTime} state = 2)) members,

						(SELECT sum(mode * beishu * actionNum - bonus) from blast_bets where {kjTime} state = 2 and
						uid in (SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
						(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) bonus_guanfang,

						(SELECT sum(mode * beishu * actionNum) from blast_bets where {kjTime} state = 2 and uid in 
						(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
						(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) tz_guanfang,

						(SELECT sum(mode * beishu * actionNum) from blast_bets where {kjTime} state = 2 and uid in 
						(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
						(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) yx_tz_guanfang,

						(SELECT count(id) from blast_bets where {kjTime} state = 2 and uid in 
						(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
						(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) dl_guanfang,


						(SELECT sum(betAmount - bonus) from tb_bets_credit where {drawTime} state = 2 and  memberId in 
						(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
						(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) bonus_xinyong,

						(SELECT sum(betAmount) from tb_bets_credit where {drawTime} state = 2 and memberId in 
						(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
						(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) tz_xinyong,

						(SELECT sum(betAmount) from tb_bets_credit where {drawTime} state = 2 and  memberId in 
						(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
						(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) yx_tz_xinyong,

						(SELECT count(id) from tb_bets_credit where {drawTime} state = 2 and memberId in 
						(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
						(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) dl_xinyong
					'''.format(kjTime=kjTime, drawTime=drawTime)
			m_sql = m_sql_s + m_str_member + m_sql_e
			xxzl_proxy = execute(m_sql)[0]
			daili = []
			for proxy in xxzl_proxy:
				Proxy = []
				for p in proxy:
					if p is None:
						p = 0
						Proxy.append(p)
					else:
						Proxy.append(p)
				DaiLi = {}
				DaiLi['uid'] = Proxy[0]
				DaiLi['username'] = Proxy[1]
				DaiLi['type'] = Proxy[2]
				DaiLi['members'] = Proxy[3]
				DaiLi['countUid'] = Proxy[7] + Proxy[11]
				DaiLi['amount'] = float(Proxy[5]) +  float(Proxy[9])
				DaiLi['betamount'] = float(Proxy[6]) + float(Proxy[10])
				DaiLi['bonus'] = float(Proxy[4]) + float(Proxy[8])
				daili.append(DaiLi)


		# 只有娛樂城
		if args['gameType'] is not None and 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in args[
			'gameName']:
			if 'kk' not in args['gameName']:
				if args['timeLower'] and not args['timeUpper']:
					timeLower = args['timeLower']
					ReckonTime = 'ReckonTime >=' + str(timeLower) + ' and'
				if not args['timeLower'] and args['timeUpper']:
					timeUpper = args['timeUpper']
					ReckonTime = 'ReckonTime <=' + str(timeUpper) + ' and'
				if args['timeLower'] and args['timeUpper']:
					timeLower = args['timeLower']
					timeUpper = args['timeUpper']
					ReckonTime = 'ReckonTime >=' + str(timeLower) + ' and ReckonTime <=' + str(timeUpper) + ' and'
				if not args['timeLower'] and not args['timeUpper']:
					ReckonTime = 'ReckonTime >=' + str(TimeLower) + ' and ReckonTime <=' + str(TimeUpper) + ' and'
				if args['gameType']:
					gameType = tuple(args['gameType'])
					if len(gameType) == 1:
						gameType = gameType + tuple(['AG-PT-KAIYUAN-101'])

				m_str_agents = '''
							(SELECT count(uid) FROM blast_members where type = 0 and isTsetPLay = 0 
							and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)) 
							and username in (SELECT PlayerName as username from tb_entertainment_city_bets_detail 
							WHERE {ReckonTime} CONCAT(ECCode,'-',childType) in {gameType})) members,

							(SELECT sum(ValidBetAmount - CusAccount) from tb_entertainment_city_bets_detail 
							where {ReckonTime} CONCAT(ECCode,'-',childType) in {gameType} and 
							PlayerName in (SELECT username FROM blast_members where type = 0 and isTsetPLay = 0 
							and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) bonus_ylc,

							(SELECT sum(ValidBetAmount) from tb_entertainment_city_bets_detail 
							where {ReckonTime} CONCAT(ECCode,'-',childType) in {gameType} and 
							PlayerName in (SELECT username FROM blast_members where type = 0 and isTsetPLay = 0 
							and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) tz_ylc,

							(SELECT sum(ValidBetAmount) from tb_entertainment_city_bets_detail 
							where {ReckonTime} CONCAT(ECCode,'-',childType) in {gameType} and 
							PlayerName in (SELECT username FROM blast_members where type = 0 and isTsetPLay = 0 
							and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) yx_tz_ylc,

							(SELECT count(id) from tb_entertainment_city_bets_detail 
							where {ReckonTime} CONCAT(ECCode,'-',childType) in {gameType} and 
							PlayerName in (SELECT username FROM blast_members where type = 0 and isTsetPLay = 0 
							and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents))) ) dl_ylc
						'''.format(ReckonTime=ReckonTime, gameType=gameType)

				m_sql = m_sql_s + m_str_agents + m_sql_e

				xxzl_proxy = execute(m_sql)[0]
				daili = []
				for proxy in xxzl_proxy:
					Proxy = []
					for p in proxy:
						if p is None:
							p = 0
							Proxy.append(p)
						else:
							Proxy.append(p)
					DaiLi = {}
					DaiLi['uid'] = Proxy[0]
					DaiLi['username'] = Proxy[1]
					DaiLi['type'] = Proxy[2]
					DaiLi['members'] = Proxy[3]
					DaiLi['countUid'] = Proxy[7]
					DaiLi['amount'] = float(Proxy[5])
					DaiLi['betamount'] = float(Proxy[6])
					DaiLi['bonus'] = float(Proxy[4])
					daili.append(DaiLi)

		# 娛樂城和kk都有
		if 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in args['gameName']:
			if 'kk' in args['gameName']:
				if args['timeLower'] and not args['timeUpper']:
					timeLower = args['timeLower']
					kjTime = 'kjTime >=' + str(timeLower) + ' and'
					drawTime = 'drawTime >=' + str(timeLower) + ' and'
					ReckonTime = 'ReckonTime >=' + str(timeLower) + ' and'
				if not args['timeLower'] and args['timeUpper']:
					timeUpper = args['timeUpper']
					kjTime = 'kjTime <=' + str(timeUpper) + ' and'
					drawTime = 'drawTime <=' + str(timeUpper) + ' and'
					ReckonTime = 'ReckonTime <=' + str(timeUpper) + ' and'
				if args['timeLower'] and args['timeUpper']:
					timeLower = args['timeLower']
					timeUpper = args['timeUpper']
					kjTime = 'kjTime >=' + str(timeLower) + ' and kjTime <=' + str(timeUpper) + ' and'
					drawTime = 'drawTime >=' + str(timeLower) + ' and drawTime <=' + str(timeUpper) + ' and'
					ReckonTime = 'ReckonTime >=' + str(timeLower) + ' and ReckonTime <=' + str(timeUpper) + ' and'
				if not args['timeLower'] and not args['timeUpper']:
					kjTime = 'kjTime >=' + str(TimeLower) + ' and kjTime <=' + str(TimeUpper) + ' and'
					drawTime = 'drawTime >=' + str(TimeLower) + ' and drawTime <=' + str(TimeUpper) + ' and'
					ReckonTime = 'ReckonTime >=' + str(TimeLower) + ' and ReckonTime <=' + str(TimeUpper) + ' and'
				if args['gameType']:
					gameType = tuple(args['gameType'])
					if len(gameType) == 1:
						gameType = gameType + tuple(['AG-PT-KAIYUAN-101'])

				m_str_member = '''					
							(SELECT count(uid) FROM blast_members where type = 0 and isTsetPLay = 0 
							and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)) 
							and username in (SELECT PlayerName as username from tb_entertainment_city_bets_detail 
							WHERE {ReckonTime} CONCAT(ECCode,'-',childType) in {gameType}
							UNION all SELECT memberUsername as username from tb_bets_credit where {drawTime} state = 2
							UNION all SELECT username as username from blast_bets where {kjTime} state = 2)) members,

							(SELECT sum(mode * beishu * actionNum - bonus) from blast_bets where {kjTime} state = 2 and
							uid in (SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
							(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) bonus_guanfang,

							(SELECT sum(mode * beishu * actionNum) from blast_bets where {kjTime} state = 2 and uid in 
							(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
							(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) tz_guanfang,

							(SELECT sum(mode * beishu * actionNum) from blast_bets where {kjTime} state = 2 and uid in 
							(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
							(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) yx_tz_guanfang,

							(SELECT count(id) from blast_bets where {kjTime} state = 2 and uid in 
							(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
							(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) dl_guanfang,


							(SELECT sum(betAmount - bonus) from tb_bets_credit where {drawTime} state = 2 and  memberId in 
							(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
							(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) bonus_xinyong,

							(SELECT sum(betAmount) from tb_bets_credit  where {drawTime} state = 2 and memberId in 
							(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
							(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) tz_xinyong,

							(SELECT sum(betAmount) from tb_bets_credit where {drawTime} state = 2 and  memberId in 
							(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
							(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) yx_tz_xinyong,

							(SELECT count(id) from tb_bets_credit where {drawTime} state = 2 and memberId in 
							(SELECT uid FROM blast_members where type = 0 and isTsetPLay = 0 and uid in 
							(SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) dl_xinyong
						'''.format(kjTime=kjTime,ReckonTime=ReckonTime, drawTime=drawTime, gameType=gameType)

				m_str_agents = '''											
							(SELECT sum(ValidBetAmount - CusAccount) from tb_entertainment_city_bets_detail 
							where {ReckonTime} CONCAT(ECCode,'-',childType) in {gameType} and 
							PlayerName in (SELECT username FROM blast_members where type = 0 and isTsetPLay = 0 
							and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) bonus_ylc,

							(SELECT sum(ValidBetAmount) from tb_entertainment_city_bets_detail 
							where {ReckonTime} CONCAT(ECCode,'-',childType) in {gameType} and 
							PlayerName in (SELECT username FROM blast_members where type = 0 and isTsetPLay = 0 
							and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) tz_ylc,

							(SELECT sum(ValidBetAmount) from tb_entertainment_city_bets_detail 
							where {ReckonTime} CONCAT(ECCode,'-',childType) in {gameType} and 
							PlayerName in (SELECT username FROM blast_members where type = 0 and isTsetPLay = 0 
							and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents)))) yx_tz_ylc,

							(SELECT count(id) from tb_entertainment_city_bets_detail 
							where {ReckonTime} CONCAT(ECCode,'-',childType) in {gameType} and 
							PlayerName in (SELECT username FROM blast_members where type = 0 and isTsetPLay = 0 
							and uid in (SELECT uid FROM blast_members where FIND_IN_SET(aa.uid,parents))) ) dl_ylc
						'''.format(ReckonTime=ReckonTime, gameType=gameType)

				m_sql = m_sql_s + m_str_member + ',' + m_str_agents + m_sql_e
				xxzl_proxy = execute(m_sql)[0]
				daili = []
				for proxy in xxzl_proxy:
					Proxy = []
					for p in proxy:
						if p is None:
							p = 0
							Proxy.append(p)
						else:
							Proxy.append(p)
					DaiLi = {}
					DaiLi['uid'] = Proxy[0]
					DaiLi['username'] = Proxy[1]
					DaiLi['type'] = Proxy[2]
					DaiLi['members'] = Proxy[3]
					DaiLi['countUid'] = Proxy[7] + Proxy[11] + Proxy[15]
					DaiLi['amount'] = float(Proxy[5] + Proxy[9]) + Proxy[13]
					DaiLi['betamount'] = float(Proxy[6] + Proxy[10]) + Proxy[14]
					DaiLi['bonus'] = float(Proxy[4] + Proxy[8]) + Proxy[12]
					daili.append(DaiLi)

		xxzl_dict = {}
		Parent = db.session.query(Member.id,Member.username,Member.type).filter(Member.username == args['memberUsername']).first()
		if Parent:
			xxzl_dict['parent_ID'] = Parent[0]
			xxzl_dict['parent_name'] = Parent[1]
			xxzl_dict['parent_type'] = Parent[2]
			if args['memberType'] is None:
				xxzl_dict['parent_ID'] = None
				xxzl_dict['parent_name'] = None
				xxzl_dict['parent_type'] = None
		else:
			xxzl_dict['parent_ID'] = None
			xxzl_dict['parent_name'] = None
			xxzl_dict['parent_type'] = None
		xxzl_dict['agensList'] = daili
		xxzl_dict['memberList'] = xx_res

		result = [xxzl_dict]
		return make_response(result)


class ExportReports(Resource):
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('timeLower', type=int)
		parser.add_argument('timeUpper', type=int)
		parser.add_argument('memberUsername', type=str)
		parser.add_argument('memberType', type=int)
		parser.add_argument('gameType', type=str)
		parser.add_argument('gameName', type=str)
		args = parser.parse_args(strict=True)

		if args['gameType'] is None:
			return make_response(error_code=400, error_message="没有选择游戏类型")
		if args['gameName'] is None:
			return make_response(error_code=400, error_message="没有选择游戏平台")
		if args['gameType']:
			args['gameType'] = ast.literal_eval(args['gameType'])
		else:
			args['gameType'] = []
		if args['gameName']:
			args['gameName'] = ast.literal_eval(args['gameName'])
		else:
			args['gameName'] = []
		if args['memberType'] == 0:
			if not args['memberUsername']:
				return make_response(error_code=400, error_message="会员不能为空")
		if args['memberType'] == 1:
			if not args['memberUsername']:
				return make_response(error_code=400, error_message="代理不能为空")
		# 驗證代理或者會員是否存在
		if args['memberUsername'] and args['memberType'] == 1:
			arg = [1, 9, 10, 11]
			member = db.session.query(Member.id).filter(Member.username == args['memberUsername'],
														Member.type.in_(arg)).first()
			if member is None:
				if args['memberType'] == 1:
					return make_response(error_code=400, error_message="该代理不存在")

		TimeLower = -2208981211
		TimeUpper = 32503687932
		if args['memberType'] == 0 and args['memberUsername']:
			member = db.session.query(Member.id).filter(Member.username == args['memberUsername'],
														Member.type==0).first()
			if member is None:
				return make_response(error_code=400, error_message="该会员不存在")
			name = args['memberUsername']
			if args['timeLower'] and not args['timeUpper']:
				timeLower = args['timeLower']
				kjTime = 'kjTime >=' + str(timeLower) + ' and'
				drawTime = 'drawTime >=' + str(timeLower) + ' and'
				ReckonTime = 'ReckonTime >=' + str(timeLower) + ' and'
			if not args['timeLower'] and args['timeUpper']:
				timeUpper = args['timeUpper']
				kjTime = 'kjTime <=' + str(timeUpper) + ' and'
				drawTime = 'drawTime <=' + str(timeUpper) + ' and'
				ReckonTime = 'ReckonTime <=' + str(timeUpper) + ' and'
			if args['timeLower'] and args['timeUpper']:
				timeLower = args['timeLower']
				timeUpper = args['timeUpper']
				kjTime = 'kjTime >=' + str(timeLower) + ' and kjTime <=' + str(timeUpper) + ' and'
				drawTime = 'drawTime >=' + str(timeLower) + ' and drawTime <=' + str(timeUpper) + ' and'
				ReckonTime = 'ReckonTime >=' + str(timeLower) + ' and ReckonTime <=' + str(timeUpper) + ' and'
			if not args['timeLower'] and not args['timeUpper']:
				kjTime = 'kjTime >=' + str(TimeLower) + ' and kjTime <=' + str(TimeUpper) + ' and'
				drawTime = 'drawTime >=' + str(TimeLower) + ' and drawTime <=' + str(TimeUpper) + ' and'
				ReckonTime = 'ReckonTime >=' + str(TimeLower) + ' and ReckonTime <=' + str(TimeUpper) + ' and'
			if args['gameType']:
				gameType = tuple(args['gameType'])
				if len(gameType) == 1:
					gameType = gameType + tuple(['AG-PT-KAIYUAN-101'])

			# 只有kk
			if 'kk' in args['gameName'] and 'AG' not in args['gameName'] and 'PT' not in args[
				'gameName'] and 'KAIYUAN' not in args['gameName']:
				m_sql = '''SELECT {name},sum(betAmount),sum(bonus) ,count(username),
						(select parentsInfo from blast_members where username = {name})aa,
						(select levelName from blast_member_level WHERE id = (SELECT grade FROM blast_members where  username = {name})) levelName
						FROM 
						(SELECT username,(mode * beishu * actionNum) as betAmount,(mode * beishu * actionNum - bonus) bonus from blast_bets
						WHERE {kjTime} state= 2 and username ={name}
						UNION ALL
						SELECT memberUsername as username,betAmount,(betAmount - bonus) as bonus from tb_bets_credit
						WHERE {drawTime} state = 2 and memberUsername ={name})BETS GROUP BY 
						username'''.format(kjTime=kjTime, drawTime=drawTime, name="'"+str(name)+"'")
				tjbb_excel = execute(m_sql)[0]

			# 只有娛樂城
			if args['gameType'] is not None and 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in \
					args['gameName']:
				if 'kk' not in args['gameName']:
					m_sql = '''SELECT {name},sum(betAmount),sum(bonus) ,count(username),
							(select parentsInfo from blast_members where username = {name})aa,
							(select levelName from blast_member_level WHERE id = (SELECT grade FROM blast_members where  username = {name})) levelName
							FROM
							(SELECT PlayerName as username,ValidBetAmount as betAmount,(ValidBetAmount - CusAccount) as bonus from tb_entertainment_city_bets_detail
							WHERE {ReckonTime} PlayerName =  {name}
							and CONCAT(ECCode,'-',childType) in {gameType}) BETS GROUP BY
							username'''.format(ReckonTime=ReckonTime, gameType=gameType, name="'"+str(name)+"'")
					tjbb_excel = execute(m_sql)[0]
			# 娛樂城和kk都有
			if 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in args['gameName']:
				if 'kk' in args['gameName']:
					m_sql = '''SELECT {name},sum(betAmount),sum(bonus) ,count(username),
							(select parentsInfo from blast_members where username = {name})aa,
							(select levelName from blast_member_level WHERE id = (SELECT grade FROM blast_members where  username = {name})) levelName
							FROM 
							(SELECT username,(mode * beishu * actionNum) as betAmount,(mode * beishu * actionNum - bonus) bonus from blast_bets
							WHERE {kjTime} state = 2 and username = {name}
							UNION ALL
							SELECT memberUsername as username,betAmount,(betAmount - bonus) as bonus from tb_bets_credit
							WHERE {drawTime} state = 2 and memberUsername = {name}
							UNION ALL
							SELECT PlayerName as username,ValidBetAmount as betAmount,(ValidBetAmount - CusAccount) as bonus from tb_entertainment_city_bets_detail
							WHERE {ReckonTime} PlayerName = {name}
							and CONCAT(ECCode,'-',childType) in {gameType}) BETS GROUP BY 
							username'''.format(kjTime=kjTime, ReckonTime=ReckonTime, drawTime=drawTime,gameType=gameType, name="'"+str(name)+"'")
					tjbb_excel = execute(m_sql)[0]

			from openpyxl import Workbook
			import os, time
			workbook = Workbook()
			worksheet = workbook.active
			title = ['代理层级', '会员', '会员等级', '单量', '投注额', '有效投注', '损益']
			worksheet.append(title)
			for tjbb in tjbb_excel:
				result = []
				str1 = tjbb[4]
				str1 = str1.replace(',', '->')
				result.append(str1)
				result.append(tjbb[0])
				result.append(tjbb[5])
				result.append(tjbb[3])
				result.append('%.2f' % tjbb[1])
				result.append('%.2f' % tjbb[1])
				result.append('%.2f' % tjbb[2])
				worksheet.append(result)
			filename = '统计报表-' + str(int(time.time())) + '.xlsx'
			workbook.save(os.path.join(current_app.static_folder, filename))
			return make_response([{
				'success': True,
				'resultFilename': filename,
			}])

		if args['memberType'] is None:
			m_sql_e = '''
					SELECT username FROM blast_members WHERE type = 0 and isTsetPLay = 0
					'''
		else:
			m_sql_e = '''
					SELECT username FROM blast_members WHERE FIND_IN_SET({},parents) and type = 0 and isTsetPLay = 0
					'''.format(member[0])

		# 只有kk
		if 'kk' in args['gameName'] and 'AG' not in args['gameName'] and 'PT' not in args[
			'gameName'] and 'KAIYUAN' not in args['gameName']:
			if args['timeLower'] and not args['timeUpper']:
				timeLower = args['timeLower']
				kjTime = 'kjTime >=' + str(timeLower) + ' and'
				drawTime = 'drawTime >=' + str(timeLower) + ' and'
			if not args['timeLower'] and args['timeUpper']:
				timeUpper = args['timeUpper']
				kjTime = 'kjTime <=' + str(timeUpper) + ' and'
				drawTime = 'drawTime <=' + str(timeUpper) + ' and'
			if args['timeLower'] and args['timeUpper']:
				timeLower = args['timeLower']
				timeUpper = args['timeUpper']
				kjTime = 'kjTime >=' + str(timeLower) + ' and kjTime <=' + str(timeUpper) + ' and'
				drawTime = 'drawTime >=' + str(timeLower) + ' and drawTime <=' + str(timeUpper) + ' and'
			if not args['timeLower'] and not args['timeUpper']:
				kjTime = 'kjTime >=' + str(TimeLower) + ' and kjTime <=' + str(TimeUpper) + ' and'
				drawTime = 'drawTime >=' + str(TimeLower) + ' and drawTime <=' + str(TimeUpper) + ' and'


			m_sql = '''SELECT username,sum(betAmount),sum(bonus) ,count(username),
						(select parentsInfo from blast_members where username = BETS.username)aa,
						(select levelName from blast_member_level WHERE id = (SELECT grade FROM blast_members where  username = BETS.username)) levelName
						FROM 
						(SELECT username,(mode * beishu * actionNum) as betAmount,(mode * beishu * actionNum - bonus) bonus from blast_bets
						WHERE {kjTime} state= 2 and username in ({m_sql_e})
						UNION ALL
						SELECT memberUsername as username,betAmount,(betAmount - bonus) as bonus from tb_bets_credit
						WHERE {drawTime} state = 2 and memberUsername in ({m_sql_e}))BETS GROUP BY 
						username'''.format(kjTime=kjTime, drawTime=drawTime, m_sql_e=m_sql_e)
			tjbb_excel = execute(m_sql)[0]

		# 只有娛樂城
		if args['gameType'] is not None and 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in args['gameName']:
			if 'kk' not in args['gameName']:
				if args['timeLower'] and not args['timeUpper']:
					timeLower = args['timeLower']
					ReckonTime = 'ReckonTime >=' + str(timeLower) + ' and'
				if not args['timeLower'] and args['timeUpper']:
					timeUpper = args['timeUpper']
					ReckonTime = 'ReckonTime <=' + str(timeUpper) + ' and'
				if args['timeLower'] and args['timeUpper']:
					timeLower = args['timeLower']
					timeUpper = args['timeUpper']
					ReckonTime = 'ReckonTime >=' + str(timeLower) + ' and ReckonTime <=' + str(timeUpper) + ' and'
				if not args['timeLower'] and not args['timeUpper']:
					ReckonTime = 'ReckonTime >=' + str(TimeLower) + ' and ReckonTime <=' + str(TimeUpper) + ' and'
				if args['gameType']:
					gameType = tuple(args['gameType'])
					if len(gameType) == 1:
						gameType = gameType + tuple(['AG-PT-KAIYUAN-101'])


				m_sql = '''SELECT username,sum(betAmount),sum(bonus) ,count(username),
						(select parentsInfo from blast_members where username = BETS.username)aa,
						(select levelName from blast_member_level WHERE id = (SELECT grade FROM blast_members where  username = BETS.username)) levelName
						FROM
						(SELECT PlayerName as username,ValidBetAmount as betAmount,(ValidBetAmount - CusAccount) as bonus from tb_entertainment_city_bets_detail
						WHERE {ReckonTime} PlayerName in ({m_sql_e})
						and CONCAT(ECCode,'-',childType) in {gameType}) BETS GROUP BY
						username'''.format(ReckonTime=ReckonTime, gameType=gameType, m_sql_e=m_sql_e)

				tjbb_excel = execute(m_sql)[0]

		# 娛樂城和kk都有
		if 'AG' in args['gameName'] or 'PT' in args['gameName'] or 'KAIYUAN' in args['gameName']:
			if 'kk' in args['gameName']:
				if args['timeLower'] and not args['timeUpper']:
					timeLower = args['timeLower']
					kjTime = 'kjTime >=' + str(timeLower) + ' and'
					drawTime = 'drawTime >=' + str(timeLower) + ' and'
					ReckonTime = 'ReckonTime >=' + str(timeLower) + ' and'
				if not args['timeLower'] and args['timeUpper']:
					timeUpper = args['timeUpper']
					kjTime = 'kjTime <=' + str(timeUpper) + ' and'
					drawTime = 'drawTime <=' + str(timeUpper) + ' and'
					ReckonTime = 'ReckonTime <=' + str(timeUpper) + ' and'
				if args['timeLower'] and args['timeUpper']:
					timeLower = args['timeLower']
					timeUpper = args['timeUpper']
					kjTime = 'kjTime >=' + str(timeLower) + ' and kjTime <=' + str(timeUpper) + ' and'
					drawTime = 'drawTime >=' + str(timeLower) + ' and drawTime <=' + str(timeUpper) + ' and'
					ReckonTime = 'ReckonTime >=' + str(timeLower) + ' and ReckonTime <=' + str(timeUpper) + ' and'
				if not args['timeLower'] and not args['timeUpper']:
					kjTime = 'kjTime >=' + str(TimeLower) + ' and kjTime <=' + str(TimeUpper) + ' and'
					drawTime = 'drawTime >=' + str(TimeLower) + ' and drawTime <=' + str(TimeUpper) + ' and'
					ReckonTime = 'ReckonTime >=' + str(TimeLower) + ' and ReckonTime <=' + str(TimeUpper) + ' and'
				if args['gameType']:
					gameType = tuple(args['gameType'])
					if len(gameType) == 1:
						gameType = gameType + tuple(['AG-PT-KAIYUAN-101'])

				m_sql = '''SELECT username,sum(betAmount),sum(bonus) ,count(username),
						(select parentsInfo from blast_members where username = BETS.username)aa,
						(select levelName from blast_member_level WHERE id = (SELECT grade FROM blast_members where  username = BETS.username)) levelName
						FROM 
						(SELECT username,(mode * beishu * actionNum) as betAmount,(mode * beishu * actionNum - bonus) bonus from blast_bets
						WHERE {kjTime} state = 2 and username in ({m_sql_e})
						UNION ALL
						SELECT memberUsername as username,betAmount,(betAmount - bonus) as bonus from tb_bets_credit
						WHERE {drawTime} state = 2 and memberUsername in ({m_sql_e})
						UNION ALL
						SELECT PlayerName as username,ValidBetAmount as betAmount,(ValidBetAmount - CusAccount) as bonus from tb_entertainment_city_bets_detail
						WHERE {ReckonTime} PlayerName in ({m_sql_e}) 
						and CONCAT(ECCode,'-',childType)  in {gameType}) BETS GROUP BY 
						username'''.format(kjTime=kjTime,ReckonTime=ReckonTime, drawTime=drawTime, gameType=gameType, m_sql_e=m_sql_e)
				tjbb_excel = execute(m_sql)[0]

		from openpyxl import Workbook
		import os, time
		workbook = Workbook()
		worksheet = workbook.active
		title = ['代理层级', '会员', '会员等级', '单量', '投注额', '有效投注', '损益']
		worksheet.append(title)
		for tjbb in tjbb_excel:
			result = []
			str1 = tjbb[4]
			str1 = str1.replace(',', '->')
			result.append(str1)
			result.append(tjbb[0])
			result.append(tjbb[5])
			result.append(tjbb[3])
			result.append('%.2f' % tjbb[1])
			result.append('%.2f' % tjbb[1])
			result.append('%.2f' % tjbb[2])
			worksheet.append(result)
		filename = '统计报表-' + str(int(time.time())) + '.xlsx'
		workbook.save(os.path.join(current_app.static_folder, filename))

		return make_response([{
			'success': True,
			'resultFilename': filename,
		}])


class HomeReports(Resource):

	@marshal_with(make_marshal_fields({
		'profitAndLossDay1': fields.Integer(default=0),
		'profitAndLossDay2': fields.Integer(default=0),
		'profitAndLossDay3': fields.Integer(default=0),
		'profitAndLossDay4': fields.Integer(default=0),
		'profitAndLossDay5': fields.Integer(default=0),
		'profitAndLossDay6': fields.Integer(default=0),
		'profitAndLossDay7': fields.Integer(default=0),

		'vaildBetAmountDay1': fields.Integer(default=0),
		'vaildBetAmountDay2': fields.Integer(default=0),
		'vaildBetAmountDay3': fields.Integer(default=0),
		'vaildBetAmountDay4': fields.Integer(default=0),
		'vaildBetAmountDay5': fields.Integer(default=0),
		'vaildBetAmountDay6': fields.Integer(default=0),
		'vaildBetAmountDay7': fields.Integer(default=0),

		'numberOfBetsDay1': fields.Integer(default=0),
		'numberOfBetsDay2': fields.Integer(default=0),
		'numberOfBetsDay3': fields.Integer(default=0),
		'numberOfBetsDay4': fields.Integer(default=0),
		'numberOfBetsDay5': fields.Integer(default=0),
		'numberOfBetsDay6': fields.Integer(default=0),
		'numberOfBetsDay7': fields.Integer(default=0),

		'numberOfOnlineMembersDay1': fields.Integer(default=0),
		'numberOfOnlineMembersDay2': fields.Integer(default=0),
		'numberOfOnlineMembersDay3': fields.Integer(default=0),
		'numberOfOnlineMembersDay4': fields.Integer(default=0),
		'numberOfOnlineMembersDay5': fields.Integer(default=0),
		'numberOfOnlineMembersDay6': fields.Integer(default=0),
		'numberOfOnlineMembersDay7': fields.Integer(default=0),

		'numberOfAgentsToday': fields.Integer(default=0),
		'numberOfAgentsYestoday': fields.Integer(default=0),
		'numberOfAgentsCurrentWeek': fields.Integer(default=0),
		'numberOfAgentsLastWeek': fields.Integer(default=0),
		'numberOfAgentsCurrentMonth': fields.Integer(default=0),
		'numberOfAgentsLastMonth': fields.Integer(default=0),

		'numberOfAgentsTotalToday': fields.Integer(default=0),
		'numberOfAgentsTotalYestoday': fields.Integer(default=0),
		'numberOfAgentsTotalCurrentWeek': fields.Integer(default=0),
		'numberOfAgentsTotalLastWeek': fields.Integer(default=0),
		'numberOfAgentsTotalCurrentMonth': fields.Integer(default=0),
		'numberOfAgentsTotalLastMonth': fields.Integer(default=0),

		'numberOfNewMembersToday': fields.Integer(default=0),
		'numberOfNewMembersYestoday': fields.Integer(default=0),
		'numberOfNewMembersCurrentWeek': fields.Integer(default=0),
		'numberOfNewMembersLastWeek': fields.Integer(default=0),
		'numberOfNewMembersCurrentMonth': fields.Integer(default=0),
		'numberOfNewMembersLastMonth': fields.Integer(default=0),

		'numberOfNewMembersWithDepositToday': fields.Integer(default=0),
		'numberOfNewMembersWithDepositYestoday': fields.Integer(default=0),
		'numberOfNewMembersWithDepositCurrentWeek': fields.Integer(default=0),
		'numberOfNewMembersWithDepositLastWeek': fields.Integer(default=0),
		'numberOfNewMembersWithDepositCurrentMonth': fields.Integer(default=0),
		'numberOfNewMembersWithDepositLastMonth': fields.Integer(default=0),

		'rebateAmountToday': fields.Integer(default=0),
		'rebateAmountYestoday': fields.Integer(default=0),
		'rebateAmountCurrentWeek': fields.Integer(default=0),
		'rebateAmountLastWeek': fields.Integer(default=0),
		'rebateAmountCurrentMonth': fields.Integer(default=0),
		'rebateAmountLastMonth': fields.Integer(default=0),

		'numberOfMembersWithRebateToday': fields.Integer(default=0),
		'numberOfMembersWithRebateYestoday': fields.Integer(default=0),
		'numberOfMembersWithRebateCurrentWeek': fields.Integer(default=0),
		'numberOfMembersWithRebateLastWeek': fields.Integer(default=0),
		'numberOfMembersWithRebateCurrentMonth': fields.Integer(default=0),
		'numberOfMembersWithRebateLastMonth': fields.Integer(default=0),

		'betAmountToday': fields.Integer(default=0),
		'betAmountYestoday': fields.Integer(default=0),
		'betAmountCurrentWeek': fields.Integer(default=0),
		'betAmountLastWeek': fields.Integer(default=0),
		'betAmountCurrentMonth': fields.Integer(default=0),
		'betAmountLastMonth': fields.Integer(default=0),

		'betProfitAndLossToday': fields.Integer(default=0),
		'betProfitAndLossYestoday': fields.Integer(default=0),
		'betProfitAndLossCurrentWeek': fields.Integer(default=0),
		'betProfitAndLossLastWeek': fields.Integer(default=0),
		'betProfitAndLossCurrentMonth': fields.Integer(default=0),
		'betProfitAndLossLastMonth': fields.Integer(default=0),

		'depositAmountToday': fields.Integer(default=0),
		'depositAmountYestoday': fields.Integer(default=0),
		'depositAmountCurrentWeek': fields.Integer(default=0),
		'depositAmountLastWeek': fields.Integer(default=0),
		'depositAmountCurrentMonth': fields.Integer(default=0),
		'depositAmountLastMonth': fields.Integer(default=0),

		'numberOfMembersWithDepositToday': fields.Integer(default=0),
		'numberOfMembersWithDepositYestoday': fields.Integer(default=0),
		'numberOfMembersWithDepositCurrentWeek': fields.Integer(default=0),
		'numberOfMembersWithDepositLastWeek': fields.Integer(default=0),
		'numberOfMembersWithDepositCurrentMonth': fields.Integer(default=0),
		'numberOfMembersWithDepositLastMonth': fields.Integer(default=0),

		'withdrawalAmountToday': fields.Integer(default=0),
		'withdrawalAmountYestoday': fields.Integer(default=0),
		'withdrawalAmountCurrentWeek': fields.Integer(default=0),
		'withdrawalAmountLastWeek': fields.Integer(default=0),
		'withdrawalAmountCurrentMonth': fields.Integer(default=0),
		'withdrawalAmountLastMonth': fields.Integer(default=0),

		'numberOfMembersWithWithdrawalToday': fields.Integer(default=0),
		'numberOfMembersWithWithdrawalYestoday': fields.Integer(default=0),
		'numberOfMembersWithWithdrawalCurrentWeek': fields.Integer(default=0),
		'numberOfMembersWithWithdrawalLastWeek': fields.Integer(default=0),
		'numberOfMembersWithWithdrawalCurrentMonth': fields.Integer(default=0),
		'numberOfMembersWithWithdrawalLastMonth': fields.Integer(default=0),

		'incomeToday': fields.Integer(default=0),
		'incomeYestoday': fields.Integer(default=0),
		'incomeCurrentWeek': fields.Integer(default=0),
		'incomeLastWeek': fields.Integer(default=0),
		'incomeCurrentMonth': fields.Integer(default=0),
		'incomeLastMonth': fields.Integer(default=0),

		'today_start': fields.Integer,
		'today_end': fields.Integer,
		'yesterday_start': fields.Integer,
		'yesterday_end': fields.Integer,
		'thisweek_start': fields.Integer,
		'thisweek_end': fields.Integer,
		'lastweek_start': fields.Integer,
		'lastweek_end': fields.Integer,
		'thismonth_start': fields.Integer,
		'thismonth_end': fields.Integer,
		'lastmonth_start': fields.Integer,
		'lastmonth_end': fields.Integer,

		'day1': fields.Integer,
		'day2': fields.Integer,
		'day3': fields.Integer,
		'day4': fields.Integer,
		'day5': fields.Integer,
		'day6': fields.Integer,
		'day7': fields.Integer,
	}))
	def get(self):
		import random
		'*****************************************今日***************************************************'
		'''今日时间'''

		today = datetime.date.today()
		zeroPointToday = int(time.mktime(today.timetuple()))
		endPointToday = zeroPointToday + SECONDS_PER_DAY
		'''代理资讯'''
		agentsum = db.session.query(
			func.count(Member.username)
		).filter(
			Member.agentsTime >= zeroPointToday,
			Member.agentsTime < endPointToday,
			Member.type == 1
		).first()[0]
		agentstotal = db.session.query(
			func.count(Member.username)
		).filter(
			Member.agentsTime >= zeroPointToday,
			Member.agentsTime < endPointToday,
			Member.type == 9
		).first()[0]

		'''新进会员'''
		m_args = db.session.query(
			Deposit.memberId
		).filter(
			Deposit.auditTime >= zeroPointToday,
			Deposit.auditTime < endPointToday,
			Deposit.isAcdemen == 1,
			Deposit.status == 2
		).subquery()
		membersum = db.session.query(
			func.count(Member.username)
		).filter(
			Member.registrationTime >= zeroPointToday,
			Member.registrationTime < endPointToday,
			Member.type == 0,
			Member.isTsetPLay == 0
		).first()[0]
		memberaccount = db.session.query(
			func.count(Member.username)
		).filter(
			Member.registrationTime >= zeroPointToday,
			Member.registrationTime < endPointToday,
			Member.type == 0,
			Member.id.in_(m_args),
			Member.isTsetPLay == 0
		).first()[0]

		'''返水资讯'''
		members = db.session.query(Member.id).filter(Member.isTsetPLay == 0).subquery()
		fsamount = db.session.query(
			func.sum(MemberAccountChangeRecord.amount),
		).filter(
			MemberAccountChangeRecord.time >= zeroPointToday,
			MemberAccountChangeRecord.time < endPointToday,
			MemberAccountChangeRecord.memberId.in_(members),
			MemberAccountChangeRecord.accountChangeType.in_([2,122])
		).all()
		if fsamount:
			fsamount = fsamount[0][0]
		else:
			fsamount = 0
		conlog = db.session.query(
			MemberAccountChangeRecord.memberId
		).filter(
			MemberAccountChangeRecord.time >= zeroPointToday,
			MemberAccountChangeRecord.time < endPointToday,
			MemberAccountChangeRecord.accountChangeType.in_([2, 122])
		).subquery()
		fssum = db.session.query(
			func.count(Member.username)
		).filter(
			Member.isTsetPLay == 0,
			Member.id.in_(conlog)
		).all()
		if fssum:
			fssum = fssum[0][0]
		else:
			fssum = 0




		'''投注资讯'''
		members = db.session.query(
			Member.username
		).filter(
			Member.type == 0,
			Member.isTsetPLay == 0
		).subquery()
		betsAccount_guan = db.session.query(
			func.sum(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label('betAmount')
		).filter(
			BlastBets.kjTime >= zeroPointToday,
			BlastBets.kjTime < endPointToday,
			BlastBets.state == 2,
			BlastBets.username.in_(members)
		)
		betsAccount_xinyong = db.session.query(
			func.sum(BlastBetsCredit.betAmount).label('betAmount')
		).filter(
			BlastBetsCredit.drawTime >= zeroPointToday,
			BlastBetsCredit.drawTime < endPointToday,
			BlastBetsCredit.state == 2,
			BlastBetsCredit.memberUsername.in_(members)
		)
		betsAccount_city = db.session.query(
			func.sum(EntertainmentCityBetsDetail.ValidBetAmount).label('betAmount')
		).filter(
			EntertainmentCityBetsDetail.ReckonTime >= zeroPointToday,
			EntertainmentCityBetsDetail.ReckonTime < endPointToday,
			EntertainmentCityBetsDetail.PlayerName.in_(members)
		)
		result = union_all(betsAccount_guan, betsAccount_xinyong,betsAccount_city)
		user_alias = aliased(result, name='user_alias')
		betsAccount = db.session.query(func.sum(user_alias.c.betAmount)).first()[0]

		betsprofitandloss_guan = db.session.query(
			func.sum(BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum - BlastBets.bonus).label(
				'betAmountWin')
		).filter(
			BlastBets.kjTime >= zeroPointToday,
			BlastBets.kjTime < endPointToday,
			BlastBets.state == 2,
			BlastBets.username.in_(members)
		)
		betsprofitandloss_xinyong = db.session.query(
			func.sum(BlastBetsCredit.betAmount - BlastBetsCredit.bonus).label('betAmountWin')
		).filter(
			BlastBetsCredit.drawTime >= zeroPointToday,
			BlastBetsCredit.drawTime < endPointToday,
			BlastBetsCredit.state == 2,
			BlastBetsCredit.memberUsername.in_(members)
		)
		betsprofitandloss_city = db.session.query(
			func.sum(EntertainmentCityBetsDetail.ValidBetAmount - EntertainmentCityBetsDetail.CusAccount).label('betAmountWin')
		).filter(
			EntertainmentCityBetsDetail.ReckonTime >= zeroPointToday,
			EntertainmentCityBetsDetail.ReckonTime < endPointToday,
			EntertainmentCityBetsDetail.PlayerName.in_(members)
		)
		results = union_all(betsprofitandloss_guan, betsprofitandloss_xinyong,betsprofitandloss_city)
		user_alias_s = aliased(results, name='user_alias_s')
		betsprofitandloss = db.session.query(func.sum(user_alias_s.c.betAmountWin)).first()[0]

		members = db.session.query(
			Member.id
		).filter(
			Member.type == 0,
			Member.isTsetPLay == 0
		).subquery()


		'''存款资讯'''
		m_args = db.session.query(
			Deposit.memberId
		).filter(
			Deposit.auditTime >= zeroPointToday,
			Deposit.auditTime < endPointToday,
			Deposit.isAcdemen == 1,
			Deposit.status == 2
		).subquery()

		todaydepositNum = db.session.query(
			func.count(Member.username)
		).filter(
			Member.type == 0,
			Member.id.in_(m_args),
			Member.isTsetPLay == 0
		).first()[0]
		todaydepositAmount = db.session.query(
			func.sum(Deposit.applicationAmount)
		).filter(
			Deposit.auditTime >= zeroPointToday,
			Deposit.auditTime < endPointToday,
			Deposit.isAcdemen == 1,
			Deposit.status == 2,
			Deposit.memberId.in_(members)
		).all()
		if todaydepositAmount:
			todaydepositAmount = todaydepositAmount[0][0]
		else:
			todaydepositAmount = 0
		if todaydepositAmount == None:
			todaydepositAmount = 0

		'''取款资讯'''
		m_args = db.session.query(
			Withdrawal.memberId
		).filter(
			Withdrawal.auditTime >= zeroPointToday,
			Withdrawal.auditTime < endPointToday,
			Withdrawal.isAcdemen == 1,
			Withdrawal.status == 2
		).subquery()

		todaywithdrawalNum = db.session.query(
			func.count(Member.username)
		).filter(
			Member.type == 0,
			Member.id.in_(m_args),
			Member.isTsetPLay == 0
		).first()[0]
		todaywithdrawalAmount = db.session.query(
			func.sum(Withdrawal.withdrawalAmount)
		).filter(
			Withdrawal.auditTime >= zeroPointToday,
			Withdrawal.auditTime < endPointToday,
			Withdrawal.isAcdemen == 1,
			Withdrawal.status == 2,
			Withdrawal.memberId.in_(members)
		).all()
		if todaywithdrawalAmount:
			todaywithdrawalAmount = todaywithdrawalAmount[0][0]
		else:
			todaywithdrawalAmount = 0
		if todaywithdrawalAmount == None:
			todaywithdrawalAmount = 0
		'''总资讯'''
		sumAccount = todaydepositAmount - todaywithdrawalAmount

		'*****************************************昨日***************************************************'
		yesterday = str(datetime.date.today() - datetime.timedelta(days=1))

		yesterday_set = set()
		yesterday_set.add(Resports.audiTimes == yesterday)
		m_args_one = Resports().get(yesterday_set)
		if m_args_one:
			yesterdayagensSum = m_args_one.agensSum
			yesterdaytotalAgents = m_args_one.totalAgents
			yesterdaymemberSum = m_args_one.memberSum
			yesterdaymemberAccount = m_args_one.memberAccount
			yesterdayrebateAmount = m_args_one.rebateAmount
			yesterdayrebateMembers = m_args_one.rebateMembers
			yesterdaybetAmount = m_args_one.betAmount
			yesterdaybetAmountwin = m_args_one.betAmountwin
			yesterdaydepositAmounts = m_args_one.depositAmounts
			yesterdaynumberDeposit = m_args_one.numberDeposit
			yesterdaywithdrawalAmounts = m_args_one.withdrawalAmounts
			yesterdaynumberWithdrawal = m_args_one.numberWithdrawal
			yesterdaytotalRevenue = m_args_one.totalRevenue
		else:
			yesterdayagensSum = 0
			yesterdaytotalAgents = 0
			yesterdaymemberSum = 0
			yesterdaymemberAccount = 0
			yesterdayrebateAmount = 0
			yesterdayrebateMembers = 0
			yesterdaybetAmount = 0
			yesterdaybetAmountwin = 0
			yesterdaydepositAmounts = 0
			yesterdaynumberDeposit = 0
			yesterdaywithdrawalAmounts = 0
			yesterdaynumberWithdrawal = 0
			yesterdaytotalRevenue = 0
		'*****************************************本周***************************************************'
		this_week_start = (datetime.datetime.now() - timedelta(days=datetime.datetime.now().weekday())).strftime(
			'%Y-%m-%d')
		this_week_end = (datetime.datetime.now() + timedelta(days=6 - datetime.datetime.now().weekday())).strftime(
			'%Y-%m-%d')
		this_week = db.session.query(
			func.sum(Resports.withdrawalAmounts).label('thisweek_withdrawalAmounts'),
			func.sum(Resports.numberWithdrawal).label('thisweek_numberWithdrawal'),
			func.sum(Resports.depositAmounts).label('thisweek_depositAmounts'),
			func.sum(Resports.numberDeposit).label('thisweek_numberDeposit'),
			func.sum(Resports.totalRevenue).label('thisweek_totalRevenue'),
			func.sum(Resports.betAmount).label('thisweek_betAmount'),
			func.sum(Resports.betAmountwin).label('thisweek_betAmountwin'),
			func.sum(Resports.rebateAmount).label('thisweek_rebateAmount'),
			func.sum(Resports.rebateMembers).label('thisweek_rebateMembers'),
			func.sum(Resports.memberSum).label('thisweek_memberSum'),
			func.sum(Resports.memberAccount).label('thisweek_memberAccount'),
			func.sum(Resports.agensSum).label('thisweek_agensSum'),
			func.sum(Resports.totalAgents).label('thisweek_totalAgents'),
		).filter(Resports.audiTimes >= this_week_start, Resports.audiTimes <= this_week_end).first()
		'*****************************************上周***************************************************'

		last_week_start = (datetime.datetime.now() - timedelta(days=datetime.datetime.now().weekday() + 7)).strftime(
			'%Y-%m-%d')
		last_week_end = (datetime.datetime.now() - timedelta(days=datetime.datetime.now().weekday() + 1)).strftime(
			'%Y-%m-%d')

		last_week = db.session.query(
			func.sum(Resports.withdrawalAmounts).label('last_week_withdrawalAmounts'),
			func.sum(Resports.numberWithdrawal).label('last_week_numberWithdrawal'),
			func.sum(Resports.depositAmounts).label('last_week_depositAmounts'),
			func.sum(Resports.numberDeposit).label('last_week_numberDeposit'),
			func.sum(Resports.totalRevenue).label('last_week_totalRevenue'),
			func.sum(Resports.betAmount).label('last_week_betAmount'),
			func.sum(Resports.betAmountwin).label('last_week_betAmountwin'),
			func.sum(Resports.rebateAmount).label('last_week_rebateAmount'),
			func.sum(Resports.rebateMembers).label('last_week_rebateMembers'),
			func.sum(Resports.memberSum).label('last_week_memberSum'),
			func.sum(Resports.memberAccount).label('last_week_memberAccount'),
			func.sum(Resports.agensSum).label('last_week_agensSum'),
			func.sum(Resports.totalAgents).label('last_week_totalAgents'),
		).filter(Resports.audiTimes >= last_week_start, Resports.audiTimes <= last_week_end).first()
		'*****************************************本月***************************************************'
		this_month_start = (datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, 1)).strftime(
			'%Y-%m-%d')
		this_month_end = (
					datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month + 1, 1) - timedelta(
				days=1)).strftime(
			'%Y-%m-%d')
		this_month = db.session.query(
			func.sum(Resports.withdrawalAmounts).label('this_month_withdrawalAmounts'),
			func.sum(Resports.numberWithdrawal).label('this_month_numberWithdrawal'),
			func.sum(Resports.depositAmounts).label('this_month_depositAmounts'),
			func.sum(Resports.numberDeposit).label('this_month_numberDeposit'),
			func.sum(Resports.totalRevenue).label('this_month_totalRevenue'),
			func.sum(Resports.betAmount).label('this_month_betAmount'),
			func.sum(Resports.betAmountwin).label('this_month_betAmountwin'),
			func.sum(Resports.rebateAmount).label('this_month_rebateAmount'),
			func.sum(Resports.rebateMembers).label('this_month_rebateMembers'),
			func.sum(Resports.memberSum).label('this_month_memberSum'),
			func.sum(Resports.memberAccount).label('this_month_memberAccount'),
			func.sum(Resports.agensSum).label('this_month_agensSum'),
			func.sum(Resports.totalAgents).label('this_month_totalAgents'),
		).filter(Resports.audiTimes >= this_month_start, Resports.audiTimes <= this_month_end).first()
		'*****************************************上月***************************************************'
		last_month_end = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, 1) - timedelta(
			days=1)
		last_month_start = (datetime.datetime(last_month_end.year, last_month_end.month, 1)).strftime(
			'%Y-%m-%d')
		last_month_end = last_month_end.strftime(
			'%Y-%m-%d')
		last_month = db.session.query(
			func.sum(Resports.withdrawalAmounts).label('last_month_withdrawalAmounts'),
			func.sum(Resports.numberWithdrawal).label('last_month_numberWithdrawal'),
			func.sum(Resports.depositAmounts).label('last_month_depositAmounts'),
			func.sum(Resports.numberDeposit).label('last_month_numberDeposit'),
			func.sum(Resports.totalRevenue).label('last_month_totalRevenue'),
			func.sum(Resports.betAmount).label('last_month_betAmount'),
			func.sum(Resports.betAmountwin).label('last_month_betAmountwin'),
			func.sum(Resports.rebateAmount).label('last_month_rebateAmount'),
			func.sum(Resports.rebateMembers).label('last_month_rebateMembers'),
			func.sum(Resports.memberSum).label('last_month_memberSum'),
			func.sum(Resports.memberAccount).label('last_month_memberAccount'),
			func.sum(Resports.agensSum).label('last_month_agensSum'),
			func.sum(Resports.totalAgents).label('last_month_totalAgents'),
		).filter(Resports.audiTimes >= last_month_start, Resports.audiTimes <= last_month_end).first()
		'************************************获取七天对应的时间*****************************************'
		day1 = str(datetime.date.today() - datetime.timedelta(days=1))
		days1 = changeData(day1)
		day2 = str(datetime.date.today() - datetime.timedelta(days=2))
		days2 = changeData(day2)
		day3 = str(datetime.date.today() - datetime.timedelta(days=3))
		days3 = changeData(day3)
		day4 = str(datetime.date.today() - datetime.timedelta(days=4))
		days4 = changeData(day4)
		day5 = str(datetime.date.today() - datetime.timedelta(days=5))
		days5 = changeData(day5)
		day6 = str(datetime.date.today() - datetime.timedelta(days=6))
		days6 = changeData(day6)
		day7 = str(datetime.date.today() - datetime.timedelta(days=7))
		days7 = changeData(day7)

		'***************************************柱形图 图1**********************************************'
		q1 = db.session.query(Resports.betAmount.label('betAmount'), Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day1)
		q2 = db.session.query(Resports.betAmount.label('betAmount'), Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day2)
		q3 = db.session.query(Resports.betAmount.label('betAmount'), Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day3)
		q4 = db.session.query(Resports.betAmount.label('betAmount'), Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day4)
		q5 = db.session.query(Resports.betAmount.label('betAmount'), Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day5)
		q6 = db.session.query(Resports.betAmount.label('betAmount'), Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day6)
		q7 = db.session.query(Resports.betAmount.label('betAmount'), Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day7)
		results = union_all(q1, q2, q3, q4, q5, q6, q7)
		user_alias_s = aliased(results, name='user_alias_s')
		bet_day = db.session.query(user_alias_s.c.audiTimes, user_alias_s.c.betAmount).all()
		bet_day = dict(bet_day)
		if day1 in bet_day:
			vaildBetAmountDay1 = bet_day[day1]
		else:
			vaildBetAmountDay1 = 0
		if day2 in bet_day:
			vaildBetAmountDay2 = bet_day[day2]
		else:
			vaildBetAmountDay2 = 0
		if day3 in bet_day:
			vaildBetAmountDay3 = bet_day[day3]
		else:
			vaildBetAmountDay3 = 0
		if day4 in bet_day:
			vaildBetAmountDay4 = bet_day[day4]
		else:
			vaildBetAmountDay4 = 0
		if day5 in bet_day:
			vaildBetAmountDay5 = bet_day[day5]
		else:
			vaildBetAmountDay5 = 0
		if day6 in bet_day:
			vaildBetAmountDay6 = bet_day[day6]
		else:
			vaildBetAmountDay6 = 0
		if day7 in bet_day:
			vaildBetAmountDay7 = bet_day[day7]
		else:
			vaildBetAmountDay7 = 0
		'***************************************柱形图 图2**********************************************'
		q1 = db.session.query(Resports.betAmountwin.label('betAmountwin'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day1)
		q2 = db.session.query(Resports.betAmountwin.label('betAmountwin'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day2)
		q3 = db.session.query(Resports.betAmountwin.label('betAmountwin'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day3)
		q4 = db.session.query(Resports.betAmountwin.label('betAmountwin'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day4)
		q5 = db.session.query(Resports.betAmountwin.label('betAmountwin'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day5)
		q6 = db.session.query(Resports.betAmountwin.label('betAmountwin'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day6)
		q7 = db.session.query(Resports.betAmountwin.label('betAmountwin'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day7)
		results = union_all(q1, q2, q3, q4, q5, q6, q7)
		user_alias_s = aliased(results, name='user_alias_s')
		betAmountwin_day = db.session.query(user_alias_s.c.audiTimes, user_alias_s.c.betAmountwin).all()
		betAmountwin_day = dict(betAmountwin_day)
		if day1 in betAmountwin_day:
			profitAndLossDay1 = betAmountwin_day[day1]
		else:
			profitAndLossDay1 = 0
		if day2 in betAmountwin_day:
			profitAndLossDay2 = betAmountwin_day[day2]
		else:
			profitAndLossDay2 = 0
		if day3 in betAmountwin_day:
			profitAndLossDay3 = betAmountwin_day[day3]
		else:
			profitAndLossDay3 = 0
		if day4 in betAmountwin_day:
			profitAndLossDay4 = betAmountwin_day[day4]
		else:
			profitAndLossDay4 = 0
		if day5 in betAmountwin_day:
			profitAndLossDay5 = betAmountwin_day[day5]
		else:
			profitAndLossDay5 = 0
		if day6 in betAmountwin_day:
			profitAndLossDay6 = betAmountwin_day[day6]
		else:
			profitAndLossDay6 = 0
		if day7 in betAmountwin_day:
			profitAndLossDay7 = betAmountwin_day[day7]
		else:
			profitAndLossDay7 = 0

		'***************************************柱形图 图3**********************************************'
		q1 = db.session.query(Resports.betonceday.label('betonceday'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day1)
		q2 = db.session.query(Resports.betonceday.label('betonceday'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day2)
		q3 = db.session.query(Resports.betonceday.label('betonceday'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day3)
		q4 = db.session.query(Resports.betonceday.label('betonceday'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day4)
		q5 = db.session.query(Resports.betonceday.label('betonceday'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day5)
		q6 = db.session.query(Resports.betonceday.label('betonceday'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day6)
		q7 = db.session.query(Resports.betonceday.label('betonceday'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day7)
		results = union_all(q1, q2, q3, q4, q5, q6, q7)
		user_alias_s = aliased(results, name='user_alias_s')
		betonce_day = db.session.query(user_alias_s.c.audiTimes, user_alias_s.c.betonceday).all()
		betonce_day = dict(betonce_day)
		if day1 in betonce_day:
			numberOfBetsDay1 = betonce_day[day1]
		else:
			numberOfBetsDay1 = 0
		if day2 in betonce_day:
			numberOfBetsDay2 = betonce_day[day2]
		else:
			numberOfBetsDay2 = 0
		if day3 in betonce_day:
			numberOfBetsDay3 = betonce_day[day3]
		else:
			numberOfBetsDay3 = 0
		if day4 in betonce_day:
			numberOfBetsDay4 = betonce_day[day4]
		else:
			numberOfBetsDay4 = 0
		if day5 in betonce_day:
			numberOfBetsDay5 = betonce_day[day5]
		else:
			numberOfBetsDay5 = 0
		if day6 in betonce_day:
			numberOfBetsDay6 = betonce_day[day6]
		else:
			numberOfBetsDay6 = 0
		if day7 in betonce_day:
			numberOfBetsDay7 = betonce_day[day7]
		else:
			numberOfBetsDay7 = 0
		'***************************************柱形图 图4**********************************************'
		q1 = db.session.query(Resports.betpeople.label('betpeople'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day1)
		q2 = db.session.query(Resports.betpeople.label('betpeople'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day2)
		q3 = db.session.query(Resports.betpeople.label('betpeople'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day3)
		q4 = db.session.query(Resports.betpeople.label('betpeople'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day4)
		q5 = db.session.query(Resports.betpeople.label('betpeople'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day5)
		q6 = db.session.query(Resports.betpeople.label('betpeople'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day6)
		q7 = db.session.query(Resports.betpeople.label('betpeople'),
							  Resports.audiTimes.label('audiTimes')).filter(
			Resports.audiTimes == day7)
		results = union_all(q1, q2, q3, q4, q5, q6, q7)
		user_alias_s = aliased(results, name='user_alias_s')
		betpeople_day = db.session.query(user_alias_s.c.audiTimes, user_alias_s.c.betpeople).all()
		betpeople_day = dict(betpeople_day)
		if day1 in betpeople_day:
			numberOfOnlineMembersDay1 = betpeople_day[day1]
		else:
			numberOfOnlineMembersDay1 = 0
		if day2 in betpeople_day:
			numberOfOnlineMembersDay2 = betpeople_day[day2]
		else:
			numberOfOnlineMembersDay2 = 0
		if day3 in betpeople_day:
			numberOfOnlineMembersDay3 = betpeople_day[day3]
		else:
			numberOfOnlineMembersDay3 = 0
		if day4 in betpeople_day:
			numberOfOnlineMembersDay4 = betpeople_day[day4]
		else:
			numberOfOnlineMembersDay4 = 0
		if day5 in betpeople_day:
			numberOfOnlineMembersDay5 = betpeople_day[day5]
		else:
			numberOfOnlineMembersDay5 = 0
		if day6 in betpeople_day:
			numberOfOnlineMembersDay6 = betpeople_day[day6]
		else:
			numberOfOnlineMembersDay6 = 0
		if day7 in betpeople_day:
			numberOfOnlineMembersDay7 = betpeople_day[day7]
		else:
			numberOfOnlineMembersDay7 = 0

		m_people_sum = Resports().getDay()
		if m_people_sum:
			m_people_sum = m_people_sum[0]
			if m_people_sum:
				m_people_sum = m_people_sum[0]
			else:
				m_people_sum = (0, 0, 0, 0, 0, 0, 0, 0)
		this_week_numberWithdrawal = m_people_sum[0]
		last_week_numberWithdrawal = m_people_sum[1]
		this_month_numberWithdrawal = m_people_sum[2]
		last_month_numberWithdrawal = m_people_sum[3]
		this_week_numberDeposit = m_people_sum[4]
		last_week_numberDeposit = m_people_sum[5]
		this_month_numberDeposit = m_people_sum[6]
		last_month_numberDeposit = m_people_sum[7]

		datas = getData()
		yesterday_start = datas['yesterday_start']
		yesterday_end = datas['yesterday_end']
		thisweek_start = datas['thisweek_start']
		thisweek_end = datas['thisweek_end']
		lastweek_start = datas['lastweek_start']
		lastweek_end = datas['lastweek_end']
		thismonth_start = datas['thismonth_start']
		thismonth_end = datas['thismonth_end']
		lastmonth_start = datas['lastmonth_start']
		lastmonth_end = datas['lastmonth_end']

		if agentsum is None:
			agentsum = 0
		if this_week.thisweek_agensSum is None:
			thisweek_agensSum = 0
		else:
			thisweek_agensSum = this_week.thisweek_agensSum
		if this_month.this_month_agensSum is None:
			this_month_agensSum = 0
		else:
			this_month_agensSum = this_month.this_month_agensSum

		if agentstotal is None:
			agentstotal = 0
		if this_week.thisweek_totalAgents is None:
			thisweek_totalAgents = 0
		else:
			thisweek_totalAgents = this_week.thisweek_totalAgents
		if this_month.this_month_totalAgents is None:
			this_month_totalAgents = 0
		else:
			this_month_totalAgents = this_month.this_month_totalAgents

		if membersum is None:
			membersum = 0
		if this_week.thisweek_memberSum is None:
			thisweek_memberSum = 0
		else:
			thisweek_memberSum = this_week.thisweek_memberSum
		if this_month.this_month_memberSum is None:
			this_month_memberSum = 0
		else:
			this_month_memberSum = this_month.this_month_memberSum

		if memberaccount is None:
			memberaccount = 0
		if this_week.thisweek_memberAccount is None:
			thisweek_memberAccount = 0
		else:
			thisweek_memberAccount = this_week.thisweek_memberAccount
		if this_month.this_month_memberAccount is None:
			this_month_memberAccount = 0
		else:
			this_month_memberAccount = this_month.this_month_memberAccount

		if betsAccount is None:
			betsAccount = 0
		if this_week.thisweek_betAmount is None:
			thisweek_betAmount = 0
		else:
			thisweek_betAmount = this_week.thisweek_betAmount
		if this_month.this_month_betAmount is None:
			this_month_betAmount = 0
		else:
			this_month_betAmount = this_month.this_month_betAmount

		if betsprofitandloss is None:
			betsprofitandloss = 0
		if this_week.thisweek_betAmountwin is None:
			thisweek_betAmountwin = 0
		else:
			thisweek_betAmountwin = this_week.thisweek_betAmountwin
		if this_month.this_month_betAmountwin is None:
			this_month_betAmountwin = 0
		else:
			this_month_betAmountwin = this_month.this_month_betAmountwin

		if todaydepositAmount is None:
			todaydepositAmount = 0
		if this_week.thisweek_depositAmounts is None:
			thisweek_depositAmounts = 0
		else:
			thisweek_depositAmounts = this_week.thisweek_depositAmounts
		if this_month.this_month_depositAmounts is None:
			this_month_depositAmounts = 0
		else:
			this_month_depositAmounts = this_month.this_month_depositAmounts

		if todaywithdrawalAmount is None:
			todaywithdrawalAmount = 0
		if this_week.thisweek_withdrawalAmounts is None:
			thisweek_withdrawalAmounts = 0
		else:
			thisweek_withdrawalAmounts = this_week.thisweek_withdrawalAmounts
		if this_month.this_month_withdrawalAmounts is None:
			this_month_withdrawalAmounts = 0
		else:
			this_month_withdrawalAmounts = this_month.this_month_withdrawalAmounts

		if sumAccount is None:
			sumAccount = 0
		if this_week.thisweek_totalRevenue is None:
			thisweek_totalRevenue = 0
		else:
			thisweek_totalRevenue = this_week.thisweek_totalRevenue
		if this_month.this_month_totalRevenue is None:
			this_month_totalRevenue = 0
		else:
			this_month_totalRevenue = this_month.this_month_totalRevenue

		thisweek_betAmount = betsAccount + int(thisweek_betAmount)
		this_month_betAmount = betsAccount + int(this_month_betAmount)

		thisweek_betAmountwin = int(thisweek_betAmountwin) + betsprofitandloss
		this_month_betAmountwin = int(this_month_betAmountwin) + betsprofitandloss

		result = {
			'profitAndLossDay1': profitAndLossDay1,
			'profitAndLossDay2': profitAndLossDay2,
			'profitAndLossDay3': profitAndLossDay3,
			'profitAndLossDay4': profitAndLossDay4,
			'profitAndLossDay5': profitAndLossDay5,
			'profitAndLossDay6': profitAndLossDay6,
			'profitAndLossDay7': profitAndLossDay7,

			'vaildBetAmountDay1': vaildBetAmountDay1,
			'vaildBetAmountDay2': vaildBetAmountDay2,
			'vaildBetAmountDay3': vaildBetAmountDay3,
			'vaildBetAmountDay4': vaildBetAmountDay4,
			'vaildBetAmountDay5': vaildBetAmountDay5,
			'vaildBetAmountDay6': vaildBetAmountDay6,
			'vaildBetAmountDay7': vaildBetAmountDay7,

			'numberOfBetsDay1': numberOfBetsDay1,
			'numberOfBetsDay2': numberOfBetsDay2,
			'numberOfBetsDay3': numberOfBetsDay3,
			'numberOfBetsDay4': numberOfBetsDay4,
			'numberOfBetsDay5': numberOfBetsDay5,
			'numberOfBetsDay6': numberOfBetsDay6,
			'numberOfBetsDay7': numberOfBetsDay7,

			'numberOfOnlineMembersDay1': numberOfOnlineMembersDay1,
			'numberOfOnlineMembersDay2': numberOfOnlineMembersDay2,
			'numberOfOnlineMembersDay3': numberOfOnlineMembersDay3,
			'numberOfOnlineMembersDay4': numberOfOnlineMembersDay4,
			'numberOfOnlineMembersDay5': numberOfOnlineMembersDay5,
			'numberOfOnlineMembersDay6': numberOfOnlineMembersDay6,
			'numberOfOnlineMembersDay7': numberOfOnlineMembersDay7,

			'numberOfAgentsToday': agentsum,
			'numberOfAgentsYestoday': yesterdayagensSum,
			'numberOfAgentsCurrentWeek': thisweek_agensSum + agentsum,
			'numberOfAgentsLastWeek': last_week.last_week_agensSum,
			'numberOfAgentsCurrentMonth': this_month_agensSum + agentsum,
			'numberOfAgentsLastMonth': last_month.last_month_agensSum,

			'numberOfAgentsTotalToday': agentstotal,
			'numberOfAgentsTotalYestoday': yesterdaytotalAgents,
			'numberOfAgentsTotalCurrentWeek': thisweek_totalAgents + agentstotal,
			'numberOfAgentsTotalLastWeek': last_week.last_week_totalAgents,
			'numberOfAgentsTotalCurrentMonth': this_month_totalAgents + agentstotal,
			'numberOfAgentsTotalLastMonth': last_month.last_month_totalAgents,

			'numberOfNewMembersToday': membersum,
			'numberOfNewMembersYestoday': yesterdaymemberSum,
			'numberOfNewMembersCurrentWeek': thisweek_memberSum + membersum,
			'numberOfNewMembersLastWeek': last_week.last_week_memberSum,
			'numberOfNewMembersCurrentMonth': this_month_memberSum + membersum,
			'numberOfNewMembersLastMonth': last_month.last_month_memberSum,

			'numberOfNewMembersWithDepositToday': memberaccount,
			'numberOfNewMembersWithDepositYestoday': yesterdaymemberAccount,
			'numberOfNewMembersWithDepositCurrentWeek': thisweek_memberAccount + memberaccount,
			'numberOfNewMembersWithDepositLastWeek': last_week.last_week_memberAccount,
			'numberOfNewMembersWithDepositCurrentMonth': this_month_memberAccount + memberaccount,
			'numberOfNewMembersWithDepositLastMonth': last_month.last_month_memberAccount,

			'rebateAmountToday': fsamount,
			'rebateAmountYestoday': yesterdayrebateAmount,
			'rebateAmountCurrentWeek': this_week.thisweek_rebateAmount,
			'rebateAmountLastWeek': last_week.last_week_rebateAmount,
			'rebateAmountCurrentMonth': this_month.this_month_rebateAmount,
			'rebateAmountLastMonth': last_month.last_month_rebateAmount,

			'numberOfMembersWithRebateToday': fssum,
			'numberOfMembersWithRebateYestoday': yesterdayrebateMembers,
			'numberOfMembersWithRebateCurrentWeek': this_week.thisweek_rebateMembers,
			'numberOfMembersWithRebateLastWeek': last_week.last_week_rebateMembers,
			'numberOfMembersWithRebateCurrentMonth': this_month.this_month_rebateMembers,
			'numberOfMembersWithRebateLastMonth': last_month.last_month_rebateMembers,

			'betAmountToday': betsAccount,
			'betAmountYestoday': yesterdaybetAmount,
			'betAmountCurrentWeek': thisweek_betAmount,
			'betAmountLastWeek': last_week.last_week_betAmount,
			'betAmountCurrentMonth': this_month_betAmount,
			'betAmountLastMonth': last_month.last_month_betAmount,

			'betProfitAndLossToday': betsprofitandloss,
			'betProfitAndLossYestoday': yesterdaybetAmountwin,
			'betProfitAndLossCurrentWeek': thisweek_betAmountwin,
			'betProfitAndLossLastWeek': last_week.last_week_betAmountwin,
			'betProfitAndLossCurrentMonth': this_month_betAmountwin,
			'betProfitAndLossLastMonth': last_month.last_month_betAmountwin,

			'depositAmountToday': todaydepositAmount,
			'depositAmountYestoday': yesterdaydepositAmounts,
			'depositAmountCurrentWeek': thisweek_depositAmounts + todaydepositAmount,
			'depositAmountLastWeek': last_week.last_week_depositAmounts,
			'depositAmountCurrentMonth': this_month_depositAmounts + todaydepositAmount,
			'depositAmountLastMonth': last_month.last_month_depositAmounts,

			'numberOfMembersWithDepositToday': todaydepositNum,
			'numberOfMembersWithDepositYestoday': yesterdaynumberDeposit,
			'numberOfMembersWithDepositCurrentWeek': this_week_numberDeposit,
			'numberOfMembersWithDepositLastWeek': last_week_numberDeposit,
			'numberOfMembersWithDepositCurrentMonth': this_month_numberDeposit,
			'numberOfMembersWithDepositLastMonth': last_month_numberDeposit,

			'withdrawalAmountToday': todaywithdrawalAmount,
			'withdrawalAmountYestoday': yesterdaywithdrawalAmounts,
			'withdrawalAmountCurrentWeek': thisweek_withdrawalAmounts + todaywithdrawalAmount,
			'withdrawalAmountLastWeek': last_week.last_week_withdrawalAmounts,
			'withdrawalAmountCurrentMonth': this_month_withdrawalAmounts + todaywithdrawalAmount,
			'withdrawalAmountLastMonth': last_month.last_month_withdrawalAmounts,

			'numberOfMembersWithWithdrawalToday': todaywithdrawalNum,
			'numberOfMembersWithWithdrawalYestoday': yesterdaynumberWithdrawal,
			'numberOfMembersWithWithdrawalCurrentWeek': this_week_numberWithdrawal,
			'numberOfMembersWithWithdrawalLastWeek': last_week_numberWithdrawal,
			'numberOfMembersWithWithdrawalCurrentMonth': this_month_numberWithdrawal,
			'numberOfMembersWithWithdrawalLastMonth': last_month_numberWithdrawal,

			'incomeToday': sumAccount,
			'incomeYestoday': yesterdaytotalRevenue,
			'incomeCurrentWeek': thisweek_totalRevenue + sumAccount,
			'incomeLastWeek': last_week.last_week_totalRevenue,
			'incomeCurrentMonth': this_month_totalRevenue + sumAccount,
			'incomeLastMonth': last_month.last_month_totalRevenue,

			'today_start': zeroPointToday,
			'today_end': zeroPointToday,
			'yesterday_start': yesterday_start,
			'yesterday_end': yesterday_start,
			'thisweek_start': thisweek_start,
			'thisweek_end': thisweek_end - 60 * 60 * 24,
			'lastweek_start': lastweek_start,
			'lastweek_end': lastweek_end - 60 * 60 * 24,
			'thismonth_start': thismonth_start,
			'thismonth_end': thismonth_end - 60 * 60 * 24,
			'lastmonth_start': lastmonth_start,
			'lastmonth_end': lastmonth_end - 60 * 60 * 24,

			'day1': days1,
			'day2': days2,
			'day3': days3,
			'day4': days4,
			'day5': days5,
			'day6': days6,
			'day7': days7,

		}
		return make_response([result])


class NumberOfOnlineMembers(Resource):
	def get(self):
		return {
			'success': True,
			'numberOfOnlineMembers': MemberAccessLog.query.filter(MemberAccessLog.online == 1).count()
		}

