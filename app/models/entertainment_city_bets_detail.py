from . import db
from app.models.member import Member

class EntertainmentCityBetsDetail(db.Model):
    __tablename__ = 'tb_entertainment_city_bets_detail'
    id = db.Column(db.Integer, primary_key=True)
    ECCode = db.Column(db.String)
    PlayerName = db.Column(db.String)
    BillNo = db.Column(db.String)
    GameType = db.Column(db.String)
    GameTypeInfo = db.Column(db.String)
    GameCode = db.Column(db.String)
    GameCodeInfo = db.Column(db.String)
    GameName = db.Column(db.String)
    PlayType = db.Column(db.String)
    PlayTypeInfo = db.Column(db.String)
    MachineType = db.Column(db.String)
    BetAmount = db.Column(db.Float)
    ValidBetAmount = db.Column(db.Float)
    NetAmount = db.Column(db.Float)
    CusAccount = db.Column(db.Float)
    Profit = db.Column(db.Float)
    BeforeCredit = db.Column(db.Float)
    Balance = db.Column(db.Float)
    RoomID = db.Column(db.String)
    ProductID = db.Column(db.String)
    ExttxID = db.Column(db.String)
    BetTime = db.Column(db.Integer)
    ReckonTime = db.Column(db.Integer)
    Flag = db.Column(db.String)
    Currency = db.Column(db.String)
    TableCode = db.Column(db.String)
    BetIP = db.Column(db.String)
    RecalcuTime = db.Column(db.Integer)
    PlatformType = db.Column(db.String)
    Remark = db.Column(db.String)
    Round = db.Column(db.String)
    Result = db.Column(db.String)
    DeviceType = db.Column(db.String)
    CreateDateTime = db.Column(db.Integer)
    UpdateDateTime = db.Column(db.Integer)
    extension = db.Column(db.String)
    childType = db.Column(db.Integer)
    childCode = db.Column(db.String)
    bet = db.Column(db.Float)
    insertTime = db.Column(db.Integer)
    def getGroupData(self,startDateTime,endDateTime):
        m_sql = 'SET SESSION group_concat_max_len = 809600;'
        db.session.execute(m_sql)
        m_sql = '''select concat('[',group_concat('"',BillNo,'"'),']'),ECCode,childType from (
                    select ECCode,childType,BillNo from tb_entertainment_city_bets_detail where 
                    insertTime >=%s and insertTime <=%s) a GROUP BY ECCode,childType
                '''%(startDateTime,endDateTime)
        m_data = db.session.execute(m_sql)
        return m_data

    def getCityInfo(self,critern_city):
        result = db.session.query(
            Member.id.label('memberId'),
            EntertainmentCityBetsDetail.PlayerName,
            EntertainmentCityBetsDetail.ECCode,
            EntertainmentCityBetsDetail.childType,
            EntertainmentCityBetsDetail.GameTypeInfo,
            EntertainmentCityBetsDetail.BetTime,
            EntertainmentCityBetsDetail.BetAmount,
            EntertainmentCityBetsDetail.ReckonTime,
            EntertainmentCityBetsDetail.CusAccount,
            EntertainmentCityBetsDetail.ValidBetAmount,

            EntertainmentCityBetsDetail.BillNo,
            EntertainmentCityBetsDetail.GameCodeInfo,
            EntertainmentCityBetsDetail.GameName,
            EntertainmentCityBetsDetail.PlayTypeInfo,
            EntertainmentCityBetsDetail.MachineType,
            EntertainmentCityBetsDetail.NetAmount,
            EntertainmentCityBetsDetail.BeforeCredit,
            EntertainmentCityBetsDetail.Balance,
            EntertainmentCityBetsDetail.RoomID,
            EntertainmentCityBetsDetail.ProductID,
            EntertainmentCityBetsDetail.ExttxID,
            EntertainmentCityBetsDetail.Flag,
            EntertainmentCityBetsDetail.Currency,
            EntertainmentCityBetsDetail.TableCode,
            EntertainmentCityBetsDetail.BetIP,
            EntertainmentCityBetsDetail.RecalcuTime,
            EntertainmentCityBetsDetail.PlatformType,
            EntertainmentCityBetsDetail.Remark,
            EntertainmentCityBetsDetail.Round

        ).filter(*critern_city)
        result = result.outerjoin(Member, Member.username == EntertainmentCityBetsDetail.PlayerName)
        result = result.all()
        return result

'''    
    def text(self):
        try:
            res = db.session.query(EntertainmentCityBetsDetail.PlayerName,
                db.session.query(Member.id).filter(Member.username == EntertainmentCityBetsDetail.PlayerName).label("uid")).all()
            print(res)
        except Exception as e:
            print(e)
'''



        