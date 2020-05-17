from . import db
import json
import decimal, datetime
from .common.utils import execute
from sqlalchemy import literal
from app.models.blast_type import BlastType
from app.models.blast_played import BlastPlayed
from app.models.blast_played_group import BlastPlayedGroup
'''
Created on 2018年8月9日
投注记录
@author: liuyu
'''


# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/xc'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app);
class BlastBetsCredit(db.Model):
    __tablename__ = 'tb_bets_credit'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gameType = db.Column(db.Integer)
    gameIssue = db.Column(db.String)
    drawTime = db.Column(db.Integer)
    drawNumbers = db.Column(db.String)
    betRuleName = db.Column(db.String)
    betNumbers = db.Column(db.String)
    betAmount = db.Column(db.Float)
    betTime = db.Column(db.Integer)
    betHost = db.Column(db.Integer)
    bonusProp = db.Column(db.Float)
    bonus = db.Column(db.Float)
    memberId = db.Column(db.Integer)
    memberUsername = db.Column(db.String)
    isPrized = db.Column(db.Integer)
    isDeleted = db.Column(db.Integer)
    orderId = db.Column(db.String)
    playedId = db.Column(db.Integer)
    time = db.Column(db.String)
    state = db.Column(db.Integer)
    playedGroup = db.Column(db.Integer)

    def getCreditInfo(self,critern_kk_credit):
        result = db.session.query(
            BlastBetsCredit.orderId.label('numberOrderId'),
            BlastBetsCredit.memberId.label('memberId'),
            BlastBetsCredit.memberUsername.label('PlayerName'),
            literal('KK').label('ECCode'),
            literal(1001).label('childType'),
            BlastType.title.label('PlayTypeInfo'),
            BlastBetsCredit.betTime.label('BetTime'),
            BlastBetsCredit.betAmount.label('BetAmount'),
            BlastBetsCredit.drawTime.label('ReckonTime'),
            BlastBetsCredit.bonus.label('CusAccount'),
            BlastBetsCredit.betAmount.label('ValidBetAmount'),
            BlastBetsCredit.gameIssue.label('qs'),
            BlastBetsCredit.state.label('state'),
            BlastBetsCredit.betRuleName.label('wfmc'),
            literal(None).label('wfmcPlay'),
            BlastBetsCredit.betNumbers.label('xznr'),
            BlastBetsCredit.betHost.label('hyIp'),
            BlastBetsCredit.drawNumbers.label('kjjg'),
            BlastBetsCredit.bonusProp.label('pl'),
            BlastBetsCredit.isPrized.label('sfzj'),
            literal(None).label('bs'),
            literal(None).label('zs'),
            literal(None).label('fdian'),

        ).filter(*critern_kk_credit)
        result = result.outerjoin(BlastType, BlastType.id == BlastBetsCredit.gameType)
        result = result.all()

        return result

def alchemyencoder(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)


class BlastBets(db.Model):
    __tablename__ = 'blast_bets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32))
    orderId = db.Column(db.Integer)
    playedGroup = db.Column(db.Integer)
    playedId = db.Column(db.Integer)
    actionNo = db.Column(db.String(16))  # 投注期号
    actionTime = db.Column(db.Integer)  # 投注时间
    actionNum = db.Column(db.Integer)  # 投注注数
    actionData = db.Column(db.String)  # 投注号码
    wjorderId = db.Column(db.String)
    mode = db.Column(db.Numeric(10, 3))  # 模式
    beiShu = db.Column(db.Integer)  # 倍数
    amount = db.Column(db.Numeric(10, 3))  # 金额
    lotteryNo = db.Column(db.String(255))  # lotteryNo
    zjCount = db.Column(db.Integer)  # 中奖注数
    bonus = db.Column(db.Numeric(10, 3))  # 中奖金额
    betType = db.Column(db.Integer)
    type = db.Column(db.Integer)
    uid = db.Column(db.Integer)
    state = db.Column(db.Integer)
    time = db.Column(db.String)  # 模型类中新添加
    kjTime = db.Column(db.Integer)
    actionIP = db.Column(db.Integer)
    bonusProp = db.Column(db.Numeric(10, 3))
    zhuiHaoMode = db.Column(db.Integer)
    fanDian = db.Column(db.Float)

    '''
    查询投注信息
    args ：查询条件
    return : 投注信息json
    '''

    def getData(self, m_args):
        m_sql = '''select * from (select wjorderId,actionNo,(mode * beiShu * actionNum) betAmount,
                betType,actionTime,bonus zjAmount,zjCount,kjTime,lotteryNo,
                mode,state,type,uid,username,'KK' ce,'1' playType,playedId,playedGroup,
                (select groupName from blast_played_group where id = playedGroup) groupName,
                (select title from blast_type where id = blast_bets.type) typeName, 
                (select name from blast_played where id = playedId) playedName,
                (select grade from blast_members where blast_members.uid = blast_bets.uid) grade,
                (select username from blast_members m where m.uid = (select parentId from blast_members mm where mm.uid = blast_bets.uid)) pUsername,
                (select uid from blast_members m where m.uid = (select parentId from blast_members mm where mm.uid = blast_bets.uid)) pUid,
                (select isTsetPLay from blast_members mm where mm.uid = blast_bets.uid) isTsetPLay
                from blast_bets) rbb where rbb.isTsetPLay <> 1 '''
        if m_args['userList']:
            m_array = m_args['userList'].split(",")
            if m_array:
                m_sql += ' and  rbb.username in ('
                for res in m_array:
                    m_sql += '"%s",' % (res)
                m_sql = m_sql[:-1];
                m_sql += ')'

        if m_args['wjorderId']:
            m_sql += ' and  rbb.wjorderId = "%s"' % (m_args['wjorderId'])

        if m_args['actionNo'] is not None:
            m_sql += ' and  rbb.actionNo = "%s"' % (m_args['actionNo'])

        if m_args['gradeList']:
            m_array = m_args['gradeList'].split(",")
            if m_array:
                m_sql += ' and  rbb.grade in ('
                for res in m_array:
                    m_sql += '%s,' % (res)
                m_sql = m_sql[:-1];
                m_sql += ')'

        if m_args['typeList']:
            m_array = m_args['typeList'].split(",")
            if m_array:
                m_sql += ' and  rbb.type in ('
                for res in m_array:
                    m_sql += '%s,' % (res)
                m_sql = m_sql[:-1];
                m_sql += ')'

        if m_args['playedGroupId'] is not None:
            m_sql += ' and  rbb.playedGroupId = %s' % (m_args['playedGroupId'])

        if m_args['stateList']:
            m_array = m_args['stateList'].split(",")
            if m_array:
                m_sql += ' and  rbb.state in ('
                for res in m_array:
                    m_sql += '%s,' % (res)
                m_sql = m_sql[:-1];
                m_sql += ')'

        if m_args['sActionTime']:
            m_sql += ' and  rbb.actionTime >= %s' % (m_args['sActionTime'])
        if m_args['eActionTime']:
            m_sql += ' and  rbb.actionTime <= %s' % (m_args['eActionTime'])
        if m_args['pUsername']:
            m_sql += ' and  rbb.pUsername = "%s"' % (m_args['pUsername'])

        m_sql += ' union all ' + self.getCreditDataSql(m_args)
        #m_sql2 = 'select sum(betAmount),sum(zjAmount) from ( ' + m_sql + ' ) a'
        m_sql =  'select * from (' + m_sql + ') aa order by aa.actionTime desc'
        m_result = execute(m_sql, m_args['page'], m_args['pageSize'])
        #m_result2 = db.session.execute(m_sql2).first()
        m_data = m_result[0]
        if m_data:
            m_json = json.loads(json.dumps([dict(r) for r in m_data], ensure_ascii=True, default=alchemyencoder))
            m_result[0] = m_json
        return m_result

    def getCreditDataSql(self, m_args):

        m_sql = '''select * from ( select orderId wjorderId,gameIssue actionNo,betAmount,
                0 betType,betTime actionTime,bonus zjAmount, isPrized zjCount,
                drawTime kjTime,drawNumbers lotteryNo,0 mode,state,gameType type,
                memberId uid, memberUsername username,'KK' ce,'2' playType,playedId,
                (select bpgx.id from blast_played_group_xinyong bpgx where bpgx.id = 
                (select groupId from blast_played_xinyong bpx where bpx.id = tb_bets_credit.playedId)) playedGroup,
                (select bpgx.groupName from blast_played_group_xinyong bpgx where bpgx.id = 
                (select groupId from blast_played_xinyong bpx where bpx.id = tb_bets_credit.playedId)) groupName,
                (select title from blast_type where id = tb_bets_credit.gameType) typeName,
                (select name from blast_played_xinyong bpx where bpx.id = tb_bets_credit.playedId) playedName,
                (select grade from blast_members where blast_members.uid = tb_bets_credit.memberId) grade,
                (select username from blast_members m where m.uid = 
                (select parentId from blast_members mm where mm.uid = tb_bets_credit.memberId)) pUsername,
                (select uid from blast_members m where m.uid = 
                (select parentId from blast_members mm where mm.uid = tb_bets_credit.memberId)) pUid,
                (select isTsetPLay from blast_members mm where mm.uid = tb_bets_credit.memberId) isTsetPLay
                from tb_bets_credit ) rbb where rbb.isTsetPLay <> 1 '''
        if m_args['userList']:
            m_array = m_args['userList'].split(",")
            if m_array:
                m_sql += ' and  rbb.username in ('
                for res in m_array:
                    m_sql += '"%s",' % (res)
                m_sql = m_sql[:-1];
                m_sql += ')'

        if m_args['wjorderId']:
            m_sql += ' and  rbb.wjorderId = "%s"' % (m_args['wjorderId'])

        if m_args['actionNo'] is not None:
            m_sql += ' and  rbb.actionNo = "%s"' % (m_args['actionNo'])

        if m_args['gradeList']:
            m_array = m_args['gradeList'].split(",")
            if m_array:
                m_sql += ' and  rbb.grade in ('
                for res in m_array:
                    m_sql += '%s,' % (res)
                m_sql = m_sql[:-1];
                m_sql += ')'

        if m_args['typeList']:
            m_array = m_args['typeList'].split(",")
            if m_array:
                m_sql += ' and  rbb.type in ('
                for res in m_array:
                    m_sql += '%s,' % (res)
                m_sql = m_sql[:-1];
                m_sql += ')'

        if m_args['playedGroupId'] is not None:
            m_sql += ' and  rbb.playedGroupId = %s' % (m_args['playedGroupId'])

        if m_args['stateList']:
            m_array = m_args['stateList'].split(",")
            if m_array:
                m_sql += ' and  rbb.state in ('
                for res in m_array:
                    m_sql += '%s,' % (res)
                m_sql = m_sql[:-1];
                m_sql += ')'

        if m_args['sActionTime']:
            m_sql += ' and  rbb.actionTime >= %s' % (m_args['sActionTime'])
        if m_args['eActionTime']:
            m_sql += ' and  rbb.actionTime <= %s' % (m_args['eActionTime'])
        if m_args['pUsername']:
            m_sql += ' and  rbb.pUsername = "%s"' % (m_args['pUsername'])
        return m_sql


    def getBetInfo(self,critern_kk_bet):
        result = db.session.query(
            BlastBets.wjorderId.label('numberOrderId'),
            BlastBets.uid.label('memberId'),
            BlastBets.username.label('PlayerName'),
            literal('KK').label('ECCode'),
            literal(1001).label('childType'),
            BlastType.title.label('PlayTypeInfo'),
            BlastBets.actionTime.label('BetTime'),
            (BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label('BetAmount'),
            BlastBets.kjTime.label('ReckonTime'),
            BlastBets.bonus.label('CusAccount'),
            (BlastBets.mode * BlastBets.beiShu * BlastBets.actionNum).label('ValidBetAmount'),
            BlastBets.actionNo.label('qs'),
            BlastBets.state.label('state'),
            BlastPlayed.name.label('wfmc'),
            BlastPlayedGroup.groupName.label('wfmcPlay'),
            BlastBets.actionData.label('xznr'),
            BlastBets.actionIP.label('hyIp'),
            BlastBets.lotteryNo.label('kjjg'),
            BlastBets.bonusProp.label('pl'),
            BlastBets.zjCount.label('sfzj'),
            BlastBets.beiShu.label('bs'),
            BlastBets.actionNum.label('zs'),
            BlastBets.fanDian.label('fdian'),

        ).filter(*critern_kk_bet)
        result = result.outerjoin(BlastType, BlastType.id == BlastBets.type)
        result = result.outerjoin(BlastPlayed, BlastPlayed.id == BlastBets.playedId)
        result = result.outerjoin(BlastPlayedGroup, BlastPlayedGroup.id == BlastBets.playedGroup)
        result = result.all()

        return result

