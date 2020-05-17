from flask_restful.reqparse import RequestParser

#公司入款审核-------------------------------------------------------------
coinLog_parsers = RequestParser()
coinLog_parsers.add_argument('numberList',type=str, location=['form','json','args'])
coinLog_parsers.add_argument('username',type=str, location=['form','json','args'])
coinLog_parsers.add_argument('parentName',type=str, location=['form','json','args'])
coinLog_parsers.add_argument('sActionTime',type=int, location=['form','json','args'])
coinLog_parsers.add_argument('eActionTime',type=int, location=['form','json','args'])
coinLog_parsers.add_argument('sCoin',type=float, location=['form','json','args'],default=0)
coinLog_parsers.add_argument('eCoin',type=float, location=['form','json','args'])
coinLog_parsers.add_argument('gradeList',type=str, location=['form','json','args'])
coinLog_parsers.add_argument('liqTypeList',type=str, location=['form','json','args'])
coinLog_parsers.add_argument('real',type=int, location=['form','json','args'])
#页数
coinLog_parsers.add_argument('pageNum', type=int, location=['form', 'json','args'],default=1)
#页面个数
coinLog_parsers.add_argument('pageSize', type=int, location=['form', 'json','args'],default=20)



