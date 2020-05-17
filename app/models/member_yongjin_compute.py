from . import db


class MemberYongjinCompute(db.Model):
    __tablename__ = 'tb_member_yongjin'

    id = db.Column(db.Integer, primary_key=True)
    recordId = db.Column(db.Integer)
    uid = db.Column(db.Integer)
    username = db.Column(db.String)
    amount = db.Column(db.Float)  # 每个会员参与的KK平台的佣金加总
    sunyi = db.Column(db.Float)  # 每个会员参与的KK平台的损益加总
    discounts = db.Column(db.Float, default=0)  # 每个会员从代理处得到的优惠
    fanshui = db.Column(db.Float, default=0)  # 每个会员从代理处得到的返水
    ss_fanshui = db.Column(db.Float, default=0)  # 每个会员从代理处得到的时时返水
    betAmount = db.Column(db.Float)  # 总投注金额
    actionTime = db.Column(db.Integer)
    startTime = db.Column(db.String)  # 开始时间
    endTime = db.Column(db.String)  # 结束时间
    type = db.Column(db.Integer, default=1)  # 1 自营'KK' 2 娱乐城
    ec_name = db.Column(db.String)  # 娱乐城名称
    childType = db.Column(db.Integer)  # 娱乐城游戏类型
    deposits = db.Column(db.Float, default=0)  # 每个会员时间段内的总存款
    withdrawals = db.Column(db.Float, default=0)  # 每个会员时间段内的总取款
    parentId = db.Column(db.Integer)


class MemberAgentDetail(db.Model):
    __tablename__ = 'tb_member_agent'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    recordId = db.Column(db.Integer)
    username = db.Column(db.String)
    type = db.Column(db.Integer)  # 代理级别
    yongjin = db.Column(db.Float)  # 佣金
    memberCount = db.Column(db.Integer)  # 有效会员人数
    sunyi = db.Column(db.Float)  # 损益
    youhui = db.Column(db.Float, default=0)  # 优惠
    youhui_bi = db.Column(db.Float)         # 代理承担的优惠比
    fanshui = db.Column(db.Float, default=0)  # 批次返水
    fanshui_bi = db.Column(db.Float)  # 代理承担的返水比
    ss_fanshui = db.Column(db.Float, default=0)  # 时时返水
    deposits = db.Column(db.Float, default=0)  # 存款
    withdrawals = db.Column(db.Float, default=0)  # 取款
    betAmount = db.Column(db.Float, default=0)  # 有效投注额
    startTime = db.Column(db.String)
    endTime = db.Column(db.String)

class MemberAgentExport(db.Model):
    __tablename__ = 'tb_member_agent_export'

    id = db.Column(db.Integer, primary_key=True)
    recordId = db.Column(db.Integer)    # 关联tb_member_agent表,  外键
    startTime = db.Column(db.String)
    endTime = db.Column(db.String)
