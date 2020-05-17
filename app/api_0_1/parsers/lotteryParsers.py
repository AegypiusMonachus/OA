from flask_restful.reqparse import RequestParser

#开奖信息-------------------------------------------------------------
data_get_parser = RequestParser()
data_get_parser.add_argument('actionNo', type=str, location=['form', 'json','args'], required=False)
data_get_parser.add_argument('type', type=int, location=['form', 'json','args'], required=False)
data_get_parser.add_argument('sActionTime', type=int, location=['form', 'json','args'], required=False)
data_get_parser.add_argument('eActionTime', type=int, location=['form', 'json','args'], required=False)
data_get_parser.add_argument('page', type=int, location=['form', 'json','args'], required=False,default=1)
data_get_parser.add_argument('pageSize', type=int, location=['form', 'json','args'], required=False,default=30)
#系统彩-------------------------------------------------------------
dataAdmin_get_parser = RequestParser()
dataAdmin_get_parser.add_argument('username', type=str, location=['form', 'json','args'], required=False)
dataAdmin_get_parser.add_argument('actionNo', type=str, location=['form', 'json','args'], required=False)
dataAdmin_get_parser.add_argument('type', type=int, location=['form', 'json','args'], required=False)
dataAdmin_get_parser.add_argument('page', type=int, location=['form', 'json','args'], required=False,default=1)
dataAdmin_get_parser.add_argument('pageSize', type=int, location=['form', 'json','args'], required=False,default=30)
dataAdmin_get_parser.add_argument('sActionTime', type=int, location=['form', 'json','args'], required=False)
dataAdmin_get_parser.add_argument('eActionTime', type=int, location=['form', 'json','args'], required=False)
data_admin_post_parser = RequestParser()
data_admin_post_parser.add_argument('id',type=int, location=['form','json','args'], required=False)
data_admin_post_parser.add_argument('type',type=int, location=['form','json','args'], required=False)
data_admin_post_parser.add_argument('time',type=int, location=['form','json','args'], required=False)
data_admin_post_parser.add_argument('actionNo',type=str, location=['form','json','args'], required=False)
data_admin_post_parser.add_argument('data',type=str, location=['form','json','args'], required=False)
data_admin_post_parser.add_argument('uid',type=int, location=['form','json','args'], required=False)
data_admin_post_parser.add_argument('username',type=str, location=['form','json','args'], required=False)
#投注记录-------------------------------------------------------------
bets_parsers = RequestParser()
bets_parsers.add_argument('historyBet',type=int, location=['form','json','args'])
bets_parsers.add_argument('memberId',type=str, location=['form','json','args'])
bets_parsers.add_argument('agentsId', type=str, location=['form', 'json','args'])
bets_parsers.add_argument('betTimeLower',type=int, location=['form','json','args'])
bets_parsers.add_argument('betTimeUpper',type=int, location=['form','json','args'])
bets_parsers.add_argument('payoutTimeLower',type=int, location=['form','json','args'])
bets_parsers.add_argument('payoutTimeUpper',type=int, location=['form','json','args'])
bets_parsers.add_argument('playerId', type=str, location=['form', 'json','args'])
bets_parsers.add_argument('playerIdType', type=str, location=['form', 'json','args'])
bets_parsers.add_argument('betnumber', type=str, location=['form', 'json','args'])
bets_parsers.add_argument('gameId', type=str, location=['form', 'json','args'])
bets_parsers.add_argument('gameName', type=str, location=['form', 'json','args'])
bets_parsers.add_argument('gameNameLike', type=str, location=['form', 'json','args'])
bets_parsers.add_argument('status', type=int, location=['form', 'json','args'])
bets_parsers.add_argument('betAmountLower', type=int, location=['form', 'json','args'])
bets_parsers.add_argument('betAmountUpper', type=int, location=['form', 'json','args'])
bets_parsers.add_argument('betAmountLowerYx', type=int, location=['form', 'json','args'])
bets_parsers.add_argument('betAmountUpperYx', type=int, location=['form', 'json','args'])
bets_parsers.add_argument('payoutAmountLower', type=int, location=['form', 'json','args'])
bets_parsers.add_argument('payoutAmountUpper', type=int, location=['form', 'json','args'])
bets_parsers.add_argument('page', type=int, location=['form', 'json','args'],default=1)
bets_parsers.add_argument('pageSize', type=int, location=['form', 'json','args'],default=30)

#彩票-------------------------------------------------------------
type_parsers = RequestParser()
type_parsers.add_argument('title',type=str, location=['form','json','args'])
type_parsers.add_argument('groupList',type=str, location=['form','json','args'])
type_parsers.add_argument('typeList',type=str, location=['form','json','args'])
type_parsers.add_argument('enable',type=int, location=['form','json','args'])
type_parsers.add_argument('sort',type=int, location=['form','json','args'])
type_parsers.add_argument('defaultViewGroup',type=int, location=['form','json','args'])
type_parsers.add_argument('page', type=int, location=['form','form', 'json','args'],default=1)
type_parsers.add_argument('pageSize', type=int, location=['form','form', 'json','args'],default=50)

#玩法大类-------------------------------------------------------------
played_group_parsers = RequestParser()
played_group_parsers.add_argument('enable',type=int, location=['form','json','args'])
played_group_parsers.add_argument('groupName',type=str, location=['form','json','args'])
played_group_parsers.add_argument('sort',type=int, location=['form','json','args'])
played_group_parsers.add_argument('android',type=int, location=['form','json','args'])
played_group_parsers.add_argument('bdwEnable',type=int, location=['form','json','args'])
played_group_parsers.add_argument('page', type=int, location=['form', 'json','args'],default=1)
played_group_parsers.add_argument('pageSize', type=int, location=['form', 'json','args'],default=50)

#玩法赔率-------------------------------------------------------------
played_parser = RequestParser()
played_parser.add_argument('name',type=str, location=['form','json','args'], required=False)
played_parser.add_argument('android',type=int, location=['form','json','args'])
played_parser.add_argument('enable',type=int, location=['form','json','args'], required=False)
played_parser.add_argument('type',type=int, location=['form','json','args'], required=False)
played_parser.add_argument('bonusProp',type=float, location=['form','json','args'], required=False)
played_parser.add_argument('bonusPropBase',type=float, location=['form','json','args'], required=False)
played_parser.add_argument('groupId',type=int, location=['form','json','args'], required=False)
played_parser.add_argument('sort',type=int, location=['form','json','args'], required=False)
played_parser.add_argument('minCharge',type=int, location=['form','json','args'], required=False)
played_parser.add_argument('allCount',type=int, location=['form','json','args'], required=False)
played_parser.add_argument('maxCount',type=int, location=['form','json','args'], required=False)
played_parser.add_argument('simpleInfo',type=str, location=['form','json','args'], required=False)
played_parser.add_argument('info',type=str, location=['form','json','args'], required=False)
played_parser.add_argument('example',type=str, location=['form','json','args'], required=False)
played_parser.add_argument('maxCharge',type=int, location=['form','json','args'], required=False)
played_parser.add_argument('page', type=int, location=['form','form', 'json','args'],default=1)
played_parser.add_argument('pageSize', type=int, location=['form','form', 'json','args'],default=100)


#玩法大类(信用)-------------------------------------------------------------
played_group_credit_parsers = RequestParser()
played_group_credit_parsers.add_argument('enable',type=int, location=['form','json','args'])
played_group_credit_parsers.add_argument('groupName',type=str, location=['form','json','args'])
played_group_credit_parsers.add_argument('sort',type=int, location=['form','json','args'])
played_group_credit_parsers.add_argument('typename',type=str, location=['form','json','args'])
played_group_credit_parsers.add_argument('page', type=int, location=['form', 'json','args'],default=1)
played_group_credit_parsers.add_argument('pageSize', type=int, location=['form', 'json','args'],default=50)

#玩法赔率(信用)-------------------------------------------------------------
played_credit_parser = RequestParser()
played_credit_parser.add_argument('name',type=str, location=['form','json','args'], required=False)
played_credit_parser.add_argument('enable',type=int, location=['form','json','args'], required=False)
played_credit_parser.add_argument('type',type=int, location=['form','json','args'], required=False)
played_credit_parser.add_argument('bonusProp',type=float, location=['form','json','args'], required=False)
played_credit_parser.add_argument('groupId',type=int, location=['form','json','args'], required=False)
played_credit_parser.add_argument('remark',type=str, location=['form','json','args'], required=False)
played_credit_parser.add_argument('ruleName',type=str, location=['form','json','args'], required=False)
played_credit_parser.add_argument('page', type=int, location=['form', 'json','args'],default=1)
played_credit_parser.add_argument('pageSize', type=int, location=['form', 'json','args'],default=50)
played_credit_parser.add_argument('sort',type=int, location=['form','json','args'], required=False)
played_credit_parser.add_argument('minCharge',type=int, location=['form','json','args'], required=False)
played_credit_parser.add_argument('allCount',type=int, location=['form','json','args'], required=False)
played_credit_parser.add_argument('maxCount',type=int, location=['form','json','args'], required=False)
played_credit_parser.add_argument('maxCharge',type=int, location=['form','json','args'], required=False)









