
from . import db
from app.models.common.utils import *
from app.common.dataUtils import *


class Resports(db.Model):
    __tablename__ = 'tb_reports_form'

    id = db.Column('id', db.Integer(), primary_key=True)
    withdrawalAmounts = db.Column('withdrawal_amounts', db.Integer)
    numberWithdrawal = db.Column('number_withdrawal', db.Float)
    depositAmounts = db.Column('deposit_amounts', db.Integer)
    numberDeposit = db.Column('number_deposit', db.Float)
    totalRevenue = db.Column('total_revenue', db.Integer)
    betAmount = db.Column('bet_amount', db.Float)
    betAmountwin = db.Column('bet_amountwin', db.Float)
    betonceday = db.Column('bet_once_day',db.Integer)
    betpeople = db.Column('bet_people',db.Integer)
    rebateAmount = db.Column('rebate_amount', db.Float)
    rebateMembers = db.Column('rebate_members', db.Integer)
    memberSum = db.Column('member_sum',db.Integer)
    memberAccount = db.Column('member_account',db.Integer)
    agensSum = db.Column('agens_sum', db.Integer)
    totalAgents = db.Column('total_agents', db.Integer)
    audiTimes = db.Column('audi_times', db.String)
    actiontime = db.Column(db.Integer)


    def get(self,critern):
        result = db.session.query(Resports).filter(*critern).first()
        return result

    def getDay(self):
        datas = getData()
        thisweek_start = datas['thisweek_start']
        thisweek_end = datas['thisweek_end']
        lastweek_start = datas['lastweek_start']
        lastweek_end =datas['lastweek_end']
        thismonth_start = datas['thismonth_start']
        thismonth_end =datas['thismonth_end']
        lastmonth_start = datas['lastmonth_start']
        lastmonth_end = datas['lastmonth_end']



        m_sql = '''select 
                    (SELECT count(uid) from blast_members where isTsetPLay = 0 and type = 0 and uid IN(
                    SELECT * from 
                    (select uid from blast_member_cash where 
                    auditTime >= %s
                    and  
                    auditTime < %s and isAcdemen = 1 and state = 2) aa)),
                    
                    (SELECT count(uid) from blast_members where isTsetPLay = 0 and type = 0 and uid IN(
                    SELECT * from 
                    (select uid from blast_member_cash where 
                    auditTime >= %s
                    and  
                    auditTime < %s and isAcdemen = 1 and state = 2) aa)),
                    
                    (SELECT count(uid) from blast_members where isTsetPLay = 0 and type = 0 and uid IN(
                    SELECT * from 
                    (select uid from blast_member_cash where 
                    auditTime >= %s
                    and  
                    auditTime < %s and isAcdemen = 1 and state = 2) aa)),
                    
                    (SELECT count(uid) from blast_members where isTsetPLay = 0 and type = 0 and uid IN(
                    SELECT * from 
                    (select uid from blast_member_cash where 
                    auditTime >= %s
                    and  
                    auditTime < %s  and isAcdemen = 1 and state = 2) aa)),
                    
                    (SELECT count(uid) from blast_members where isTsetPLay = 0 and type = 0 and uid IN(
                    SELECT * from 
                    (SELECT uid from blast_member_recharge where 
                    auditTime >= %s
                    and  
                    auditTime < %s and isAcdemen = 1 and state = 2) aa)),
                    
                    (SELECT count(uid) from blast_members where isTsetPLay = 0 and type = 0 and uid IN(
                    SELECT * from 
                    (SELECT uid from blast_member_recharge where 
                    auditTime >= %s
                    and  
                    auditTime < %s and isAcdemen = 1 and state = 2) aa)),
                    
                    (SELECT count(uid) from blast_members where isTsetPLay = 0 and type = 0 and uid IN(
                    SELECT * from 
                    (SELECT uid from blast_member_recharge where 
                    auditTime >= %s 
                    and  
                    auditTime < %s and isAcdemen = 1 and state = 2) aa)),
                    
                    (SELECT count(uid) from blast_members where isTsetPLay = 0 and type = 0 and uid IN(
                    SELECT * from 
                    (SELECT uid from blast_member_recharge where 
                    auditTime >= %s
                    and  
                    auditTime < %s and isAcdemen = 1 and state = 2) aa))'''%(
                        thisweek_start,
                        thisweek_end,
                        lastweek_start,
                        lastweek_end,
                        thismonth_start,
                        thismonth_end,
                        lastmonth_start,
                        thismonth_start,
                        thisweek_start,
                        thisweek_end,
                        lastweek_start,
                        lastweek_end,
                        thismonth_start,
                        thismonth_end,
                        lastmonth_start,
                        thismonth_start
                    )
        m_args = execute(m_sql)
        return m_args



