from . import db


class MemberAccountChangeRecord(db.Model):
    __tablename__ = 'blast_coin_log'

    id = db.Column('id', db.Integer(), primary_key=True)
    memberId = db.Column('uid', db.Integer, db.ForeignKey('blast_members.uid'))
    memberBalance = db.Column('userCoin', db.Float)
    memberFrozenBalance = db.Column('fcoin', db.Float)
    amount = db.Column('coin', db.Float)
    lotteryType = db.Column('type', db.Integer, default=0)
    accountChangeType = db.Column('liqType', db.Integer)
    time = db.Column('actionTime', db.Integer)
    host = db.Column('actionIP', db.Integer)
    info = db.Column('info', db.String, default='')
    actionUID = db.Column(db.Integer)
    auditType = db.Column(db.Integer)
    auditCharge = db.Column('dml', db.Float)
    isAcdemen = db.Column(db.Integer)
    playedId = db.Column(db.Integer)

    # 导致账变的订单编号
    # 根据账变类型和导致账变的订单编号，可确定导致账变的订单
    orderId = db.Column('extfield0', db.String)
    rechargeid = db.Column('wjorderId', db.String)
    extfield1 = db.Column('extfield1', db.String)
    extfield2 = db.Column('extfield2', db.String)
    sxf = db.Column(db.Float)

    def insert(self, **args):
        dao = MemberAccountChangeRecord(**args)
        try:
            db.session.add(dao)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
        return dao


class Deposit(db.Model):
    __tablename__ = 'blast_member_recharge'

    id = db.Column(db.Integer, primary_key=True)
    memberId = db.Column('uid', db.Integer, db.ForeignKey('blast_members.uid'))
    username = db.Column(db.String)
    bankAccountId = db.Column('bankId', db.Integer)
    systemBankAccountId = db.Column('mBankId', db.Integer)
    number = db.Column('rechargeId', db.String)
    applicationAmount = db.Column('amount', db.Float)
    applicationTime = db.Column('actionTime', db.Integer)
    applicationHost = db.Column('actionIP', db.Integer)
    depositAmount = db.Column('rechargeAmount', db.Float, default=0)
    depositTime = db.Column('rechargeTime', db.Float)
    auditType = db.Column(db.Integer)
    auditCharge = db.Column(db.Float)
    auditUser = db.Column(db.Integer, db.ForeignKey('tb_users.id'))
    auditTime = db.Column(db.Integer)
    auditHost = db.Column(db.Integer)
    status = db.Column('state', db.Integer)
    type = db.Column(db.Integer)
    pOrderid = db.Column('p_orderid', db.String)
    msg = db.Column(db.String)
    income_type = db.Column(db.Integer)
    remitter = db.Column(db.String)
    pay_type = db.Column(db.Integer)
    isAcdemen = db.Column(db.Integer, default=1)
    sxf = db.Column(db.Float)

    @staticmethod
    def generate_number():
        rows = [row[0] for row in db.session.query(Deposit.number).all()]
        import random
        number = random.randint(100000, 999999)
        while number in rows:
            number = random.randint(100000, 999999)
        return number

    @staticmethod
    def get_deposits_after_last_withdrawal(member_id, deposit_type):
        criterion = set()
        criterion.add(Deposit.memberId == member_id)
        criterion.add(Deposit.type == deposit_type)
        last_withdrawal = Withdrawal.get_last_withdrawal(member_id, 200002)
        if last_withdrawal:
            # 用提现申请时间作为判断条件是错误的，有待协调
            criterion.add(Deposit.applicationTime > last_withdrawal.applicationTime)
        return Deposit.query.filter(*criterion).all()


class Withdrawal(db.Model):
    __tablename__ = 'blast_member_cash'

    id = db.Column(db.Integer, primary_key=True)
    memberId = db.Column('uid', db.Integer, db.ForeignKey('blast_members.uid'))
    bankId = db.Column(db.Integer, db.ForeignKey('blast_bank_list.id'), default=None)
    bankAccountName = db.Column('username', db.String, default=None)
    bankAccountNumber = db.Column('account', db.String, default=None)
    applicationAmount = db.Column('amount', db.Float, default=None)
    applicationTime = db.Column('actionTime', db.Integer, default=None)
    applicationHost = db.Column('actionIP', db.Integer)
    auditUser = db.Column(db.Integer, db.ForeignKey('tb_users.id'))
    auditTime = db.Column(db.Integer)
    auditHost = db.Column(db.Integer)
    status = db.Column('state', db.Integer, default=1)
    type = db.Column(db.Integer)
    isDelete = db.Column(db.Integer, default=0)
    withdrawalAmount = db.Column(db.Float)
    handlingCharge = db.Column(db.Float)
    administrativeCharge = db.Column(db.Float)
    discountCharge = db.Column(db.Float)
    sxf = db.Column('sxFee', db.Float)
    yhkc = db.Column('yhFee', db.Float)
    xzf = db.Column('xzFee', db.Float)
    remark = db.Column('remark', db.String)
    remarkFront = db.Column('frontRemark', db.String)
    orderID = db.Column(db.String)
    info = db.Column(db.String)
    flag = db.Column(db.Integer, default=0)
    cashId = db.Column(db.Integer)
    procTime = db.Column(db.Integer)
    actionUid = db.Column(db.Integer)
    isAcdemen = db.Column(db.Integer, default=1)

    @staticmethod
    def get_last_withdrawal(member_id, withdrawal_type):
        criterion = set()
        criterion.add(Withdrawal.memberId == member_id)
        criterion.add(Withdrawal.type == withdrawal_type)
        criterion.add(Withdrawal.status == 2)
        return Withdrawal.query.filter(*criterion).order_by(Withdrawal.applicationTime.desc()).first()

