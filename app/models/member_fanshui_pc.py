from . import db
import datetime,json
from app.models.common.utils import execute
from . import alchemyencoder

'''返水计算--批次返水'''
class MemberFanshuiPc(db.Model):
    __tablename__ = 'tb_member_fanshui_pc'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer)
    username = db.Column(db.String)
    amount = db.Column(db.Float)            #　返水金额
    betAmount = db.Column(db.Float)         # 总投注金额(天)
    pc_fsb = db.Column(db.Float)            # 批次返水比
    pc_dml = db.Column(db.Float)            # 打码量
    fsOrderId = db.Column(db.Integer)       # 返水订单ID
    state = db.Column(db.Integer)           # 状态
    actionTime = db.Column(db.Integer)      # 开始时间
    fanshuiTime = db.Column(db.String)      # 返水的时间
    ec_name = db.Column(db.String)          # 娱乐城名称
    childType = db.Column(db.Integer)       # 娱乐城游戏类型
    is_zero = db.Column(db.Integer)
    
    def getFanshuiStatistics(self,**args):
        date = datetime.datetime.now()
        endTime = date.strftime('%Y-%m-%d')
        if args['endTime']:
            endTime = args['endTime']
        # sql = '''select fanshuiTime,sum(amount) amount,count(DISTINCT username) users,actionTime  from (
        #       select * from tb_member_fanshui_pc where fanshuiTime <='%s' '''%(endTime)
        sql = '''select fanshuiTime,count(DISTINCT username) users, sum( amount ) amount, actionTime from tb_member_fanshui_pc WHERE fanshuiTime <= '%s' '''%(endTime)
        if args['startTime']:
            sql +=' and fanshuiTime >= "%s"'%(args['startTime'])
        if args['agents']:
            sql += ' and uid in (select uid from blast_members where parentId = (select uid from blast_members where username = "%s") and isTsetPLay = 0 and type = 0)'%(args['agents'])
        # sql = sql + ' )a GROUP BY fanshuiTime '
        sql = sql + ' GROUP BY fanshuiTime, actionTime '
        sql = sql +" order by fanshuiTime desc"
        result = execute(sql,args['page'],args['pageSize'])
        return result

    def getFanshuiDetail(self,**args):
        sql = '''select uid,username, CONCAT("[",GROUP_CONCAT(fs),"]") fs from (
                select uid,username,CONCAT("{",CONCAT('"',ec_name,'"',':',sum(amount)),"}") fs from tb_member_fanshui_pc 
                where fanshuiTime >= '%s' and fanshuiTime <='%s' '''%(args['startTime'],args['endTime'])

        if args['agents']:
            sql += ' and uid in (select uid from blast_members where parentId = (select uid from blast_members where username = "%s")and isTsetPLay = 0 and type = 0)'%(args['agents'])
        sql = sql + ' GROUP BY uid,ec_name,username) a group by uid,username'
        result = execute(sql,args['page'],args['pageSize'])
#         data = result[0]
#         if data:
#             mjson = json.loads(json.dumps([dict(r) for r in data], ensure_ascii=True, default=alchemyencoder))
#         result[0] = mjson
        return result
    
