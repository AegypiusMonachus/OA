from flask_restful.reqparse import RequestParser

#取款申请审核-------------------------------------------------------------
cash_parsers = RequestParser()
cash_parsers.add_argument('cashId',type=int, location=['form','json','args'])
cash_parsers.add_argument('userList',type=str, location=['form','json','args'])
cash_parsers.add_argument('gradeList',type=str, location=['form','json','args'])
cash_parsers.add_argument('sActionTime',type=int, location=['form','json','args'])
cash_parsers.add_argument('eActionTime',type=int, location=['form','json','args'])
cash_parsers.add_argument('sProcTime',type=int, location=['form','json','args'])
cash_parsers.add_argument('eProcTime',type=int, location=['form','json','args'])
cash_parsers.add_argument('sAmount',type=float, location=['form','json','args'],default=0)
cash_parsers.add_argument('eAmount',type=float, location=['form','json','args'])
cash_parsers.add_argument('stateList',type=str, location=['form','json','args'])
cash_parsers.add_argument('actionUsername',type=str, location=['form','json','args'])#处理人员
cash_parsers.add_argument('page', type=int, location=['form', 'json','args'],default=1)
cash_parsers.add_argument('pageSize', type=int, location=['form', 'json','args'],default=20)



