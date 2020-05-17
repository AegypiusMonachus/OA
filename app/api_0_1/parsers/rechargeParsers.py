from flask_restful.reqparse import RequestParser

#公司入款审核-------------------------------------------------------------
recharge_parsers = RequestParser()
recharge_parsers.add_argument('rechargeId',type=int, location=['json','args'])
recharge_parsers.add_argument('userList',type=str, location=['json','args'])
recharge_parsers.add_argument('gradeList',type=str, location=['json','args'])
recharge_parsers.add_argument('sActionTime',type=int, location=['json','args'])
recharge_parsers.add_argument('eActionTime',type=int, location=['json','args'])
recharge_parsers.add_argument('sRechargeTime',type=int, location=['json','args'])
recharge_parsers.add_argument('eRechargeTime',type=int, location=['json','args'])
recharge_parsers.add_argument('sAmount',type=float, location=['json','args'],default=0)
recharge_parsers.add_argument('eAmount',type=float, location=['json','args'])
recharge_parsers.add_argument('stateList',type=str, location=['json','args'])
recharge_parsers.add_argument('actionUsername',type=str, location=['json','args'])#处理人员
recharge_parsers.add_argument('mRelBankNameList',type=str, location=['json','args'])#银行名称
recharge_parsers.add_argument('mBankUsernameList',type=str, location=['json','args'])#银行收款人
recharge_parsers.add_argument('mBankAddressList',type=str, location=['json','args'])#银行网点
recharge_parsers.add_argument('mBankAccountList',type=str, location=['json','args'])#银行账号
recharge_parsers.add_argument('type',type=int, location=['json','args'])#类型
recharge_parsers.add_argument('page', type=int, location=['form', 'json','args'],default=1)
recharge_parsers.add_argument('pageSize', type=int, location=['form', 'json','args'],default=20)



