from flask import Blueprint

api_0_1_blueprint = Blueprint('api_0_1', __name__)

from app.auth.common import token_auth


@api_0_1_blueprint.before_request
@token_auth.login_required
def before_request():
    pass


@api_0_1_blueprint.after_request
def after_request(response):
    return response


from flask_restful import Api

api = Api(api_0_1_blueprint)

from .resources.users import (
    Users,
    CurrentUser,
    RoleTypes,
    Roles,
    Menus
)

api.add_resource(Users, '/users', '/users/<int:id>')
api.add_resource(CurrentUser, '/currentUser')
api.add_resource(RoleTypes, '/roleTypes')
api.add_resource(Roles, '/roles')
api.add_resource(Menus, '/menus')

from .resources.members import (
    Members,
    MemberPersonalInfos,
    MemberPersonalInfosRemark,
    MemberDetails,
    MemberAccessLogs,
    ExcelMemberAccessLogs,
    MemberLogs,
    MemberBatchCreateLogs,
    ExportMembers,
    ImportMembers,
    ResetPassword,
    ResetFundPassword,
    GetMembers,
    YlcOutStationBalance,
    UpdateallWallet,
    GetWallet,
    GetAllEcWallet,
    UpdateAllEcWallet
)

api.add_resource(Members, '/members', '/members/<int:id>')
api.add_resource(MemberPersonalInfos, '/members/<int:id>/personalInfo')
api.add_resource(MemberPersonalInfosRemark, '/members/<int:id>/personalInfoRemark')
api.add_resource(MemberDetails, '/members/<int:id>/details')
api.add_resource(MemberAccessLogs, '/memberAccessLogs', '/memberAccessLogs/<int:id>')
api.add_resource(ExcelMemberAccessLogs, '/ExcelMemberAccessLogs')
api.add_resource(MemberLogs, '/memberLogs')
api.add_resource(MemberBatchCreateLogs, '/memberBatchCreateLogs')
api.add_resource(ExportMembers, '/exportMembers')
api.add_resource(ImportMembers, '/importMembers')
api.add_resource(ResetPassword, '/resetMemberPassword')
api.add_resource(ResetFundPassword, '/resetMemberFundPassword')
api.add_resource(GetMembers, '/getmembers')
api.add_resource(YlcOutStationBalance, '/ylcoutstationbalance')#会员详情--监视会员钱包
api.add_resource(UpdateallWallet, '/UpdateWallet')#更新会员某个娱乐城的钱包
api.add_resource(GetWallet, '/GetWallet')#取回会员某个娱乐城的钱包
api.add_resource(GetAllEcWallet, '/GetAllEcWallet')#取回会员玩过所有娱乐城的钱包到主账户
api.add_resource(UpdateAllEcWallet, '/UpdateAllEcWallet')#更新会员玩过所有娱乐城的钱包

from .resources.agents import (
    Agents,
    AgentsTotal,
    AgentPersonalInfos,
    AgentPersonalInfosRemark,
    AgentDetails,
    DefaultAgents,
    ExportAgents,
    SearchCountMember
)

api.add_resource(Agents, '/agents', '/agents/<int:id>')
api.add_resource(AgentsTotal, '/agents/all')
api.add_resource(AgentPersonalInfos, '/agents/<int:id>/personalInfo')
api.add_resource(AgentPersonalInfosRemark, '/agents/<int:id>/personalInfoRemark')
api.add_resource(AgentDetails, '/agents/<int:id>/details')
api.add_resource(DefaultAgents, '/defaultAgents')
api.add_resource(ExportAgents, '/exportAgents', '/exportAgents/<int:id>')
api.add_resource(SearchCountMember, '/searchcountmember/<int:id>')  # 当前代理下会员总人数显示

from .resources.agent_audits import (
    AgentAudits,
    AgentAuditDetails
)

api.add_resource(AgentAudits, '/agentAudits', '/agentAudits/<int:id>')
api.add_resource(AgentAuditDetails, '/agentAudits/<int:id>/details')

from .resources.bank_accounts import (
    Banks,
    SystemBankAccountTypes,
    SystemBankAccounts,
    MemberBankAccounts,
    MemberBankAccountModificationLogs
)

api.add_resource(Banks, '/banks', '/banks/<int:id>')
api.add_resource(SystemBankAccountTypes, '/systemBankAccountTypes')
api.add_resource(SystemBankAccounts, '/sysconfig/systemBankAccounts', '/sysconfig/systemBankAccounts/<int:id>')
api.add_resource(MemberBankAccounts, '/memberBankAccounts')
api.add_resource(MemberBankAccountModificationLogs, '/memberBankAccountModificationLogs')

from .resources.deposit_audits import (
    DepositAuditTypes,
    DepositAudits
)

api.add_resource(DepositAuditTypes, '/depositAuditTypes')
api.add_resource(DepositAudits, '/depositAudits', '/depositAudits/<int:id>')

from .resources.system_deposits import (
    SystemDepositTypes,
    SystemDeposits
)

api.add_resource(SystemDepositTypes, '/systemDepositTypes')
api.add_resource(SystemDeposits, '/systemDeposits', '/systemDeposits/<string:orderId>')

from .resources.system_withdrawals import (
    SystemWithdrawalTypes,
    SystemWithdrawals
)

api.add_resource(SystemWithdrawalTypes, '/systemWithdrawalTypes')
api.add_resource(SystemWithdrawals, '/systemWithdrawals', '/systemWithdrawals/<string:orderId>')

from .resources.member_deposits import (
    MemberDepositStatus,
    MemberDeposits,
    MemberOnlinePayments,
    ExportMemberDeposits,
    ExportMemberOnlinePayments,
    GetMemberDeposits,
    GetMemberOnlinePayments
)

api.add_resource(MemberDepositStatus, '/memberDepositStatus')
api.add_resource(MemberDeposits, '/memberDeposits', '/memberDeposits/<string:orderId>')
api.add_resource(GetMemberDeposits, '/getmemberDeposits', '/getmemberDeposits/<int:id>')
api.add_resource(GetMemberOnlinePayments, '/getmemberOnlinePayments', '/getmemberOnlinePayments/<int:id>')
api.add_resource(MemberOnlinePayments, '/memberOnlinePayments', '/memberOnlinePayments/<string:orderId>')
api.add_resource(ExportMemberDeposits, '/exportMemberDeposits')
api.add_resource(ExportMemberOnlinePayments, '/exportMemberOnlinePayments')

from .resources.member_withdrawals import (
    MemberWithdrawalStatus,
    MemberWithdrawals,
    ExportMemberWithdrawals,
    SearchMoneyCount
)

api.add_resource(MemberWithdrawalStatus, '/memberWithdrawalStatus')
api.add_resource(MemberWithdrawals, '/memberWithdrawals', '/memberWithdrawals/<int:id>')
api.add_resource(ExportMemberWithdrawals, '/exportMemberWithdrawals')
api.add_resource(SearchMoneyCount, '/memberWithdrawals/searchmoneycount')

from .resources.member_account_changes import (
    MemberAccountChangeTypes,
    MemberAccountChangeRecords,
    ExportMemberAccountChangeRecords,
    GetMemberAccountChangeRecords,
    GetMemberAccountChangeRecordsAl
)

api.add_resource(MemberAccountChangeTypes, '/memberAccountChangeTypes')
api.add_resource(MemberAccountChangeRecords, '/memberAccountChangeRecords',
                 '/memberAccountChangeRecords/<string:orderId>')
api.add_resource(ExportMemberAccountChangeRecords, '/exportMemberAccountChangeRecords')
api.add_resource(GetMemberAccountChangeRecords, '/getMemberAccountChangeRecords')
api.add_resource(GetMemberAccountChangeRecordsAl, '/getMemberAccountChangeRecordsAl')

from .resources.finances import (
    RebateLogs,
    RebateLogDetails,
    RebateDetails,
    CommissionLogs,
    ExportDepositAndWithdrawal,
    ImportDiscountLogs,
    ImportDiscount
)

api.add_resource(RebateLogs, '/rebateLogs')
api.add_resource(RebateLogDetails, '/rebateLogDetails', '/rebateLogDetails/<int:id>')
api.add_resource(RebateDetails, '/rebateDetails')
api.add_resource(CommissionLogs, '/commissionLogs')
api.add_resource(ExportDepositAndWithdrawal, '/exportDepositAndWithdrawal')
api.add_resource(ImportDiscountLogs, '/importDiscountLogs')
api.add_resource(ImportDiscount, '/importDiscount')

from .resources.messages import (
	Messages,
	MessagesInbox,
	MessagesOutbox,
	MessageReceivers,
	Notices,
	NoticesPut,
	WebsiteAll,
	DiscountTypes,
	Discounts,
	Storage,
	Carousels,
	MemberRegistrationMessages,
	ImportTemplates,
	NoticeSetting,
	Searchname,
	SearchUname,
	GetMemLevel,
	MessageAll
)

api.add_resource(Messages, '/messages')
api.add_resource(MessagesInbox, '/messages/inbox')
api.add_resource(MessagesOutbox, '/messages/outbox')
api.add_resource(MessageReceivers, '/messages/receivers')
api.add_resource(Notices, '/sysconfig/frontmanage/announcements')
api.add_resource(NoticesPut, '/sysconfig/frontmanage/announcement/<int:announcementid>')
api.add_resource(NoticeSetting, '/sysconfig/frontmanage/announcements/setting',
                 '/sysconfig/frontmanage/announcements/setting/<int:id>')
api.add_resource(WebsiteAll, '/sysconfig/websites', '/sysconfig/websites/<int:id>')
api.add_resource(DiscountTypes, '/sysconfig/website/<int:websiteid>/discountTypes',
                 '/sysconfig/website/<int:websiteid>/<int:id>')
api.add_resource(Discounts, '/sysconfig/website/discounts/<int:discountid>')
api.add_resource(Storage, '/sysconfig/website/<int:websiteid>/storage')
api.add_resource(Carousels, '/sysconfig/frontmanage/slideshows')
api.add_resource(MemberRegistrationMessages, '/memberRegistrationMessages')
api.add_resource(ImportTemplates, '/importTemplates')
api.add_resource(Searchname, '/messags/searchname')
api.add_resource(SearchUname, '/messags/searchUname')
api.add_resource(GetMemLevel, '/messags/getmemlevel')
api.add_resource(MessageAll, '/messags/messageall')

from .resources.reports import (
    Reports,
    ExportReports,
    HomeReports,
    NumberOfOnlineMembers,
    getAllBetsAmount,
    StatisticalReport
)

api.add_resource(Reports, '/reports')
api.add_resource(ExportReports, '/exportReports')
api.add_resource(HomeReports, '/homeReports')
api.add_resource(NumberOfOnlineMembers, '/numberOfOnlineMembers')
api.add_resource(getAllBetsAmount, '/getAllBetsAmount')
api.add_resource(StatisticalReport, '/statisticalreport')

from .resources.lottery import (
    LotteryGroupAPI,
    LotteryDefaultViewGroupAPI,
    BetsRecordAPI,
    BetsRecordAPIInfos,
    BetsRecordAPIListTotal,
    ExcelBetsRecordAPIList,
    BlastTypeAPI,
    BlastPlayedGroupAPI,
    BlastPlayedAPI,
    BlastPlayedGroupCreditAPI,
    BlastPlayedCreditAPI
)

api.add_resource(LotteryGroupAPI, '/lottery/type')
api.add_resource(LotteryDefaultViewGroupAPI, '/lottery/defaultviewgroup')
api.add_resource(BetsRecordAPI, '/lottery/bets')
api.add_resource(BetsRecordAPIInfos, '/lottery/bets/infos')
api.add_resource(BetsRecordAPIListTotal, '/lottery/bets/total')
api.add_resource(ExcelBetsRecordAPIList, '/ExcelBetsRecordAPIList')
api.add_resource(BlastTypeAPI, '/lottery', '/lottery/<int:id>')
api.add_resource(BlastPlayedGroupAPI, '/lottery/<int:type>/playedgroup', '/lottery/<int:type>/playedgroup/<int:id>')
api.add_resource(BlastPlayedGroupCreditAPI, '/lottery/<int:type>/playedgroupcredit',
                 '/lottery/<int:type>/playedgroupcredit/<int:id>')
# api.add_resource(BlastPlayedGroupAPI, '/lottery/{int:type}/playedgroup','/lottery/{int:type}/playedgroup/<int:id>')
# api.add_resource(BlastPlayedGroupAPI, '/lottery/playedgroup', '/lottery/playedgroup/{int:type}')
api.add_resource(BlastPlayedAPI,
                 '/lottery/played/<int:groupId>',
                 '/lottery/played/<int:groupId>/<int:id>',
                 '/lottery/played/<int:groupId>/<int:id>/<int:lhid>')
api.add_resource(BlastPlayedCreditAPI,
                 '/lottery/playedcredit/<int:groupId>',
                 '/lottery/playedcredit/<int:groupId>/<int:id>',
                 '/lottery/playedcredit/<int:groupId>/<int:id>/<int:lhid>')

from app.api_0_1.resources.data import DataAPI

api.add_resource(DataAPI, '/lottery/data')

from app.api_0_1.resources.data_admin import DataAdminAPI

api.add_resource(DataAdminAPI, '/lottery/dataadmin', '/lottery/dataadmin/<int:id>')

# 系统管理 - 会员等级
from app.api_0_1.resources.member_level import MemberlevelAPI

api.add_resource(MemberlevelAPI, '/sysconfig/memberlevel', '/sysconfig/memberlevel/<int:id>')

# 系统管理 - 公司入款线上支付分类
from app.api_0_1.resources.member_level import MemberlevelSimpleAPI

api.add_resource(MemberlevelSimpleAPI, '/sysconfig/memberlevel/depositinfo/<int:id>')

# #系统管理 - 公司入款线上支付分类-获取全部的会员列表页
from app.api_0_1.resources.member_level import MemberlevelAllAPI

api.add_resource(MemberlevelAllAPI, '/sysconfig/memberlevel/all')

# 系统管理 - 线上支付
from .resources.sysadmin_online import SysadminOnlineAPI

api.add_resource(SysadminOnlineAPI, '/sysconfig/sysonline', '/sysconfig/sysonline/<int:id>')

# 系统管理 - 会员等级简单获取
from .resources.sysadmin_online import SysadminSimpleAPI

api.add_resource(SysadminSimpleAPI, '/sysconfig/memberlevel/simple')

# 系统设置 - 反水设置
from .resources.config_fanshui import (
    ConfigFanshuiAPI,
    ConfigFanshuiListAPI,
    FanAndGameType,
    FanAndGameSsType,
    FanCompute,
    GetFanshui,
    ApschedTime,
)

api.add_resource(FanAndGameType, '/sysconfig/fanshuishow')
api.add_resource(FanAndGameSsType, '/sysconfig/fanshuibi')
api.add_resource(ConfigFanshuiAPI, '/sysconfig/fanshui', '/sysconfig/fanshui/<int:id>')
api.add_resource(ConfigFanshuiListAPI, '/sysconfig/fanshuilist')
api.add_resource(FanCompute, '/sysconfig/fancompute')
api.add_resource(GetFanshui, '/sysconfig/getfanshui')
api.add_resource(ApschedTime, '/sysconfig/apschedtime')

# 系统设置 - 佣金设置
from .resources.config_yongjin import (
    ConfigYongjinAPI,
    YlcAndGametype,
    YongJinContent,
    ChangeStatus,
    # YongjinCompute,
    AgentYongjinCompute,
    AgentYongjinExport,
    AllAgentYongjinExport,
)

api.add_resource(ConfigYongjinAPI, '/sysconfig/yongjin')
api.add_resource(YlcAndGametype, '/sysconfig/yongjinshow')
api.add_resource(YongJinContent, '/sysconfig/yongjin/<int:id>')
api.add_resource(ChangeStatus, '/sysconfig/yongjin/changestatus')
# api.add_resource(YongjinCompute, '/sysconfig/yongcompute')
api.add_resource(AgentYongjinCompute, '/sysconfig/agentcompute')
api.add_resource(AgentYongjinExport, '/sysconfig/agentexport')
api.add_resource(AllAgentYongjinExport, '/sysconfig/allagentexport')


# 系统管理 - 站台系统值设置
from .resources.config_website import (
    ConfigWebsiteAPI,
    WebsiteSettings,
)

api.add_resource(ConfigWebsiteAPI, '/sysconfig/website', '/sysconfig/website/<int:id>')
api.add_resource(WebsiteSettings, '/sysconfig/websitesettings', '/sysconfig/websitesettings/<int:id>')

# 系统管理 - 会员端设置
from .resources.config_member_service import ConfigMemberServiceAPI

api.add_resource(ConfigMemberServiceAPI, '/sysconfig/memberservice', '/sysconfig/memberservice/<int:id>')

# 系统管理 - 在线支付
from .resources.banksOnline import BanksOnlineAPI

api.add_resource(BanksOnlineAPI, '/sysconfig/paymentgateway', '/sysconfig/paymentgateway/<int:id>')

from .resources.links import LinksAPI

api.add_resource(LinksAPI, '/links', '/links/<int:id>')

from .resources.links import UserLinksAPI

api.add_resource(UserLinksAPI, '/userlinks', '/userlinks/<int:id>')

# 系统设置 - 国别阻挡
from .resources.config_countries import ConfigCountriesAPI

api.add_resource(ConfigCountriesAPI, '/sysconfig/countries')

from .resources.banksOnline import PaymentGatewayAPI

api.add_resource(PaymentGatewayAPI, '/sysconfig/paymentgateway/maplist')

# from .resources.pay import PayAPI
# api.add_resource(PayAPI, '/pay/paymentgateway','/pay/<int:id>')

# from .resources.pay import MemberRecharge
# api.add_resource(MemberRecharge, '/recharge','/recharge/<int:id>')

from .resources.pay import SynchorAPI
 
api.add_resource(SynchorAPI, '/pay/synchor/<string:id>')
 
from .resources.pay import NotifyAPI
 
api.add_resource(NotifyAPI, '/pay/notify/<string:id>')

# from .resources.withdrawals import CheckDML
# api.add_resource(CheckDML, '/checkdml')

# from .resources.withdrawals import Qksq
# api.add_resource(Qksq, '/qksq')

# 系统管理-白名单
from .resources.config_iplists import ConfigIplistAPI

api.add_resource(ConfigIplistAPI, '/whitelist', '/whitelist/<int:id>')

from .resources.entertainment_city import (
    EntertainmentCityAPI,
    BalanceAPI,
    DepositAPI,
    RegisterAPI,
    WithdrawalAPI,
    ChangeAmountAPI,
    BetRecordAPI,
    LoginAPI,
    SearachTransfer
)

api.add_resource(EntertainmentCityAPI, '/entertainmentcity', '/entertainmentcity/<string:code>')  # 登录娱乐城
api.add_resource(BalanceAPI, '/entertainmentcity/<string:code>/balance')
api.add_resource(DepositAPI, '/entertainmentcity/<string:code>/deposit')
api.add_resource(RegisterAPI, '/entertainmentcity/<string:code>/register')
api.add_resource(WithdrawalAPI, '/entertainmentcity/<string:code>/withdrawal')
api.add_resource(ChangeAmountAPI, '/entertainmentcity/changeAmount')
api.add_resource(BetRecordAPI, '/entertainmentcity/<string:code>/betRecord')
api.add_resource(LoginAPI, '/entertainmentcity/<string:code>/login')
api.add_resource(SearachTransfer, '/entertainmentcity/<string:code>/checkTransfer')


from app.api_0_1.resources.pay import PayAPI

api.add_resource(PayAPI, '/pay/paymentgateway', '/pay/<int:id>')

from app.api_0_1.resources.pay import MemberRecharge

api.add_resource(MemberRecharge, '/recharge', '/recharge/<int:id>')

from app.api_0_1.resources.withdrawals import CheckDML

api.add_resource(CheckDML, '/checkdml')

from app.api_0_1.resources.withdrawals import Qksq

api.add_resource(Qksq, '/qksq')

'''娱乐城首页接口'''
from app.api_0_1.resources.entertainment_city_list import GetEntertainmentCityList,TransferSure,TransferLogDetail

api.add_resource(GetEntertainmentCityList, '/sysconfig/entertainmentcity')
api.add_resource(TransferSure, '/caiwumanager/entertainmentcity/transfersure')#财务管理-转账额度确认
api.add_resource(TransferLogDetail, '/caiwumanager/entertainmentcity/transfersure/detail')#财务管理-转账额度确认详情

'''检视历史记录查询'''
from app.api_0_1.resources.entertainment_city_list import SearchRecord

api.add_resource(SearchRecord, '/sysconfig/entertainmentcity/searchrecord')

'''取出所有钱包'''
from app.api_0_1.resources.entertainment_city_list import GetallWalletevery,TransferLog,GetYlcName,Uname

api.add_resource(GetallWalletevery, '/sysconfig/entertainmentcity/getallwallet')
api.add_resource(TransferLog, '/sysconfig/entertainmentcity/transferlog')
api.add_resource(GetYlcName, '/sysconfig/entertainmentcity/name')
api.add_resource(Uname, '/sysconfig/ylc/uname')

'''更新所有钱包'''
from app.api_0_1.resources.entertainment_city_list import UpdataallWalletEvery

api.add_resource(UpdataallWalletEvery, '/sysconfig/entertainmentcity/updataallwallet')

from app.api_0_1.resources.fanshui_query import FanshuiQuery

api.add_resource(FanshuiQuery, '/sysconfig/fanshuiquery')

from app.api_0_1.resources.member_history import OperationHistorys

api.add_resource(OperationHistorys, '/operation/historys')

from app.api_0_1.resources.member_account_changes import GetMemberAccountMoney

api.add_resource(GetMemberAccountMoney, '/memberAccountChangeRecords/getMemberAccountMoney')

from app.api_0_1.resources.member_deposits import MemberAccountChange

api.add_resource(MemberAccountChange, '/memberAccountChange/<string:orderId>')

from app.api_0_1.resources.member_withdrawals import MemberWithdrawalsChange

api.add_resource(MemberWithdrawalsChange, '/memberWithdrawalsChange/<string:orderId>')

from app.api_0_1.resources.entertainment_city_list import GetEntertainmentCityListAll
api.add_resource(GetEntertainmentCityListAll, '/memberWithdrawalsChange/all')

from app.api_0_1.resources.users import UserAuthority
api.add_resource(UserAuthority, '/user/authority')

from app.api_0_1.resources.entertainment_city_list import GetEntertainmentCityListone
api.add_resource(GetEntertainmentCityListone, '/memberWithdrawalsChange/list')

from app.api_0_1.resources.member_fanshui import MemberFanshui
api.add_resource(MemberFanshui, '/fanshui')

from app.api_0_1.resources.member_fanshui import MemberFanshuiDetail
api.add_resource(MemberFanshuiDetail, '/fanshui/detail')