
import time,json,decimal, datetime
from app.models.member_account_change import Withdrawal
from app.models import db
from flask import current_app


class Audits():
    #这条sql语句是查询一段时间内所有投注记录的综合
    m_sql_total_dml = '''
                        select sum(betAmount) total_amount from (
                        select orderId ,(mode * beiShu * actionNum) betAmount 
                        from blast_bets where uid = %s and state = 2 and actionTime >= %s and actionTime < %s
                        UNION all
                        select orderId,betAmount from 
                        tb_bets_credit where memberId = %s and state = 2 and betTime >= %s and betTime < %s 
                        UNION all
                        select BillNo orderId , ValidBetAmount betAmount from tb_entertainment_city_bets_detail where PlayerName = 
                        (select username from blast_members where uid = %s) and BetTime >= %s and BetTime < %s) a
                         '''
    '''m_sql_audits = 
                select * from (select id,uid,coin,liqType,actionTime,extfield0,dml 
                from blast_coin_log
                where uid = %s and liqType in (100001,100002,100020,900001,900003,900004,900005,900006)) a
                LEFT JOIN
                (select id yh_id,uid yh_uid,coin yh_coin,liqType yh_liqType,
                actionTime yh_actionTime,extfield0 yh_extfield0,dml yh_dml  
                from blast_coin_log
                where uid = %s and liqType in (100010,100011)) b
                on b.yh_extfield0 = a.extfield0
                where a.actionTime > %s
                order by a.actionTime 
                '''
    m_sql_audits = '''
                    select id,uid,coin,liqType,actionTime,extfield0,dml,auditType 
                    from blast_coin_log
                    where uid = %s and liqType in (100010,100011,100001,100002,100020,900001,900003,900004,900005,900006)
                    and actionTime > %s
                    order by id desc
                '''
    def audits(self,memberId):
        # 最后提现记录，已经出款的会员提现
        m_sql_level = ''' select xz_Free from blast_member_level 
        where id = (select grade from blast_members where uid = %s)'''%(memberId)
        xz_free = db.session.execute(m_sql_level).scalar()
        xz_free = xz_free if xz_free else 0
        last_withdrawal = Withdrawal.get_last_withdrawal(memberId, 200001)
        last_withdrawal_time = last_withdrawal.auditTime if last_withdrawal else 0
        m_time = int(time.time())
        '''查询最后一次取款后的所有入款信息。入款信息包括公司，线上支付和所有优惠信息'''
        m_result = db.session.execute(self.m_sql_audits%(memberId,last_withdrawal_time)).fetchall()
        m_result_json = json.loads(json.dumps([dict(r) for r in m_result],ensure_ascii=True,default=alchemyencoder))
        m_count = len(m_result_json)
        #取款后没有任何入款记录
        if m_count == 0:
            return None
        '''最后一次取款之后的第一次入款时间到当前时间的总打码量'''
        m_first_deposit_time = m_result_json[0]['actionTime']
        #m_TotalDML = db.session.execute(self.m_sql_total_dml%(memberId,m_first_deposit_time,m_time,memberId,m_first_deposit_time,m_time)).scalar()
        m_balance_dml = 0 #累计剩余dml
        m_return_data = {}
        m_return_List = []
        '''定义常量。存款总金额,优惠总金额,优惠提取所需打码量,存款提取所需打码量'''
        m_deposit_TotalAmount = 0
        m_yh_TotalAmount = 0
        m_need_total_depositdml = 0
        m_need_total_yhdml = 0
        m_sTime = 0;
        m_eTime = 0;
        m_failed_yh_count = 0 #优惠稽核失败笔数
        m_failed_yh_amount = 0#优惠扣除金额
        m_failed_deposit_count = 0#存款稽核失败笔数
        m_failed_deposit_amount = 0#扣除行政费用
        m_deposit_count = 0#总存款笔数
        m_failed_count = 0;
        m_deposit_pass = True
        m_yh_pass = True
        '''分阶段计算打码量。一笔入款到下一笔入款为一个阶段'''
        for index in range(m_count):
            m_liqType = m_result_json[index]['liqType']
            m_auditType = m_result_json[index]['auditType']
            if index == 0:
                m_sTime = m_result_json[index]['actionTime']
                m_eTime = m_time
            else:
                m_sTime = m_result_json[index]['actionTime'] 
                m_eTime = m_result_json[index-1]['actionTime']
            m_dml = db.session.execute(self.m_sql_total_dml%(memberId,m_sTime,m_eTime,memberId,m_sTime,m_eTime,memberId,m_sTime,m_eTime)).scalar()
            m_dml = float(m_dml) if m_dml else 0
            m_coin = 0
            m_yh_coin = 0
            m_deposit_dml = 0
            m_yh_dml =0
            m_kc = 0
            m_passed = True
            m_coin = m_result_json[index]['coin'] if m_result_json[index]['coin'] else 0
            m_need_dml = m_result_json[index]['dml'] if m_result_json[index]['dml'] else 0
            m_limit_dml = 0;
            '''计算稽核'''
            m_balance_dml = m_balance_dml + m_dml
            m_limit = m_balance_dml - m_need_dml
            '''判断打码量是否足够'''
            if m_limit >= 0:
                m_balance_dml = m_limit
                m_limit_dml = m_need_dml
            else:
                m_limit_dml = m_balance_dml
                m_balance_dml = 0
                m_passed = False
                
            #if m_liqType == 100001 or m_liqType == 100002 or m_liqType == 900001:
            if m_auditType == 2:
                m_deposit_count = m_deposit_count + 1
                m_deposit_TotalAmount = m_deposit_TotalAmount + m_coin
                if m_passed == False:
                    m_deposit_pass = False
                    m_failed_deposit_count = m_failed_deposit_count + 1
                    m_kc = float('%.2f'%(m_coin * xz_free))
                    m_failed_deposit_amount = m_failed_deposit_amount + m_kc
            elif m_auditType == 3:
                if m_passed == False:
                    m_yh_pass = False
                    m_failed_yh_count = m_failed_yh_count + 1
                    m_failed_yh_amount = m_failed_yh_amount + m_coin
                    m_kc = m_coin
                    m_yh_TotalAmount = m_yh_TotalAmount + m_coin
            else:
                #if m_liqType == 100001 or m_liqType == 100002 or m_liqType == 900001:
                m_deposit_count = m_deposit_count + 1
                m_deposit_TotalAmount = m_deposit_TotalAmount + m_coin
            m_result_json[index]['auditType'] = m_auditType
            m_result_json[index]['limit_dml'] = float('%.2f'%(m_limit_dml))
            m_result_json[index]['dml'] = float('%.2f'%(m_dml))
            m_result_json[index]['need_dml'] = float('%.2f'%(m_need_dml))
            m_result_json[index]['startTime'] = m_sTime
            m_result_json[index]['endTime'] = m_eTime
            m_result_json[index]['passed'] = m_passed
            m_result_json[index]['kc'] = m_kc
#             m_return_List.append(m_result_json[index])
            m_return_List.append(m_result_json[index])
        m_return_data['total_amount'] = m_deposit_TotalAmount
        m_return_data['total_yh_amount'] = m_yh_TotalAmount
        m_return_data['deposit_pass'] = m_deposit_pass
        m_return_data['yh_pass'] = m_yh_pass
        m_return_data['failed_yh_count'] = m_failed_yh_count
        m_return_data['failed_yh_amount'] = m_failed_yh_amount
        m_return_data['failed_deposit_count'] = m_failed_deposit_count
        m_return_data['failed_deposit_amount'] = m_failed_deposit_amount
        m_return_data['deposit_count'] = m_deposit_count
        #m_return_List.reverse()
        m_return_data['audits_list'] = m_return_List
        current_app.logger.info('%s会员即时稽核审核 ：%s'%(memberId,m_return_data))
        return m_return_data
        
def alchemyencoder(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)   
    
    
#     def audits(self,memberId):
#         # 最后提现记录，已经出款的会员提现
#         m_sql_level = ''' select xz_Free from blast_member_level 
#         where id = (select grade from blast_members where uid = %s)'''%(memberId)
#         xz_free = db.session.execute(m_sql_level).scalar()
#         xz_free = xz_free if xz_free else 0
#         last_withdrawal = Withdrawal.get_last_withdrawal(memberId, 200001)
#         last_withdrawal_time = last_withdrawal.auditTime if last_withdrawal else 0
#         m_time = int(time.time())
#         '''查询最后一次取款后的所有入款信息。入款信息包括公司，线上支付和所有优惠信息'''
#         m_result = db.session.execute(self.m_sql_audits%(memberId,last_withdrawal_time)).fetchall()
#         m_result_json = json.loads(json.dumps([dict(r) for r in m_result],ensure_ascii=True,default=alchemyencoder))
#         m_count = len(m_result_json)
#         #取款后没有任何入款记录
#         if m_count == 0:
#             return None
#         '''最后一次取款之后的第一次入款时间到当前时间的总打码量'''
#         m_first_deposit_time = m_result_json[0]['actionTime']
#         m_TotalDML = db.session.execute(self.m_sql_total_dml%(memberId,m_first_deposit_time,m_time,memberId,m_first_deposit_time,m_time)).scalar()
#         m_TotalDML = float(m_TotalDML) if m_TotalDML else 0
#         m_TotalDML_oper = m_TotalDML
#         m_return_data = {}
#         m_return_List = []
#         '''定义常量。存款总金额,优惠总金额,优惠提取所需打码量,存款提取所需打码量'''
#         m_deposit_TotalAmount = 0
#         m_yh_TotalAmount = 0
#         m_need_total_depositdml = 0
#         m_need_total_yhdml = 0
#         m_sTime = 0;
#         m_eTime = 0;
#         m_failed_yh_count = 0 #优惠稽核失败笔数
#         m_failed_yh_amount = 0#优惠扣除金额
#         m_failed_deposit_count = 0#存款稽核失败笔数
#         m_failed_deposit_amount = 0#扣除行政费用
#         m_deposit_count = 0#总存款笔数
#         m_failed_count = 0;
#         m_deposit_pass = True
#         m_yh_pass = True
#         '''分阶段计算打码量。一笔入款到下一笔入款为一个阶段'''
#         for index in range(m_count):
#             m_liqType = m_result_json[index]['liqType']
#             if index == m_count-1:
#                 m_sTime = m_result_json[index]['actionTime']
#                 m_eTime = m_time
#             else:
#                 m_sTime = m_result_json[index]['actionTime']
#                 m_eTime = m_result_json[index+1]['actionTime']
#             m_dml = db.session.execute(self.m_sql_total_dml%(memberId,m_sTime,m_eTime,memberId,m_sTime,m_eTime)).scalar()
#             m_all_dml = db.session.execute(self.m_sql_total_dml%(memberId,m_sTime,m_time,memberId,m_sTime,m_time)).scalar()
#             m_dml = float(m_dml) if m_dml else 0
#             m_all_dml = float(m_all_dml) if m_all_dml else 0
#             m_coin = 0;
#             m_yh_coin = 0;
#             m_deposit_dml = 0;
#             m_yh_dml =0;
#             m_kc = 0;
#             m_passed = True
#             m_TotalDML_oper = m_dml + m_all_dml
#             '''计算存款稽核'''
#             if m_liqType == 100001 or m_liqType == 100002 or m_liqType == 900001:
#                 m_deposit_count = m_deposit_count + 1
#                 m_coin = m_result_json[index]['coin'] if m_result_json[index]['coin'] else 0
#                 m_deposit_dml = m_result_json[index]['dml'] if m_result_json[index]['dml'] else 0
#                 m_TotalDML_oper = m_TotalDML_oper - m_deposit_dml
#                 if m_TotalDML_oper < 0:
#                     m_passed = False
#                     m_deposit_pass = False
#                     m_failed_deposit_count = m_failed_deposit_count + 1
#                     m_kc = float('%.2f'%(m_coin * xz_free))
#                     m_failed_deposit_amount = m_failed_deposit_amount + m_kc
#                     
#             else:
#                 m_yh_coin = m_result_json[index]['coin'] if m_result_json[index]['coin'] else 0
#                 m_yh_dml = m_result_json[index]['dml'] if m_result_json[index]['dml'] else 0
#                 m_TotalDML_oper = m_TotalDML_oper - m_yh_dml
#                 if m_TotalDML_oper < 0:
#                     m_passed = False
#                     m_yh_pass = False
#                     m_failed_yh_count = m_failed_yh_count + 1
#                     m_failed_yh_amount = m_failed_yh_amount + m_yh_coin
#                     m_kc = m_yh_coin
#                     
#             m_deposit_TotalAmount = m_deposit_TotalAmount + m_coin
#             m_yh_TotalAmount = m_yh_TotalAmount + m_yh_coin
#             m_need_total_yhdml = m_need_total_yhdml + m_yh_dml
#             m_need_total_depositdml = m_need_total_depositdml + m_deposit_dml
#             m_result_json[index]['limit_dml'] = float(m_dml)
#             m_result_json[index]['startTime'] = m_sTime
#             m_result_json[index]['endTime'] = m_eTime
#             m_result_json[index]['passed'] = m_passed
#             m_result_json[index]['kc'] = m_kc
# #             m_return_List.append(m_result_json[index])
#             m_return_List.insert(0,m_result_json[index])
#         m_return_data['total_dml'] = m_TotalDML
#         m_return_data['total_amount'] = m_deposit_TotalAmount
#         m_return_data['total_yh_amount'] = m_yh_TotalAmount
#         m_return_data['need_yh_dml'] = m_need_total_yhdml
#         m_return_data['need_deposit_dml'] = m_need_total_depositdml
#         m_return_data['deposit_pass'] = m_deposit_pass
#         m_return_data['yh_pass'] = m_yh_pass
#         m_return_data['failed_yh_count'] = m_failed_yh_count
#         m_return_data['failed_yh_amount'] = m_failed_yh_amount
#         m_return_data['failed_deposit_count'] = m_failed_deposit_count
#         m_return_data['failed_deposit_amount'] = m_failed_deposit_amount
#         m_return_data['deposit_count'] = m_deposit_count
#         #m_return_List.reverse()
#         m_return_data['audits_list'] = m_return_List
#         current_app.logger.info('%s会员即时稽核审核 ：%s'%(memberId,m_return_data))
#         return m_return_data
#    