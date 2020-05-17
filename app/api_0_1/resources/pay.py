from flask_restful import Resource
from flask import make_response,redirect,Response,g
from flask_restful.reqparse import RequestParser
from app.common import utils
from app.models.sysadmin_online import SysadminOnline
from app.models.payment import Payment
from app.gateway import GatewaytFactory
from flask_restful import request
from app.models.member import Member
from app.log import paylogger


'''
根据用户等级查询可用的支付网关
'''
class PayAPI(Resource):
	from app.auth.common import token_auth
	decorators = [token_auth.login_required]
	def get(self): 
		if not hasattr(g, 'current_member'):
			return {
			'errorCode': "9999",
			'errorMsg': "用戶未登录",
			'success': False
			}
# 		grade = g.current_member.levelConfig;
# 		print("%s用户查询支付网关用户等级是%s"%(g.current_member.username,grade))
		m_data = SysadminOnline().gatewayByGrade(g.current_member.username)
		return {
			'data': m_data,
			'success': True
		}
	
	def post(self,id):
		parser = RequestParser(trim=True)
		parser.add_argument('amount', type=float)
		parser.add_argument('pay_type', type=int)
		parser.add_argument('bank_type', type=str)
		m_args = parser.parse_args(strict=True)
		if not hasattr(g, 'current_member'):
			return {
			'errorCode': "9999",
			'errorMsg': "用戶未登录",
			'success': False
			}
		uid = g.current_member.id
		member = Member.query.filter(Member.id == uid).first()
		status = member.status
		if status == 2:
			m_html = '''
						<body class="notfound">
						<div class="wrapper">
							<div class="big">页面不见了！</div>
							<div>该用户钱包已经被冻结</div>
						<div>
						</body>
			            '''
		if status == 0:
			m_html = '''
						<body class="notfound">
						<div class="wrapper">
							<div class="big">页面不见了！</div>
							<div>该用户已被禁用</div>
						<div>
						</body>
			            '''
			m_response = make_response(m_html)
			m_response.headers["Content-type"]="text/html;charset=UTF-8"
			return m_response

		paylogger.info("%s用户使用线上支付%s"%(g.current_member.id,m_args['amount']))
		realIp = request.remote_addr
		ip = utils.host_to_value(realIp)
		m_res = Payment().pay(id,m_args,g.current_member.id,g.current_member.username,ip,realIp)
		paylogger.info("请求html------------------------")
		paylogger.info(m_res)
		paylogger.info("请求html------------------------")
		m_response = make_response(m_res)
		m_response.headers["Content-type"]="text/html;charset=UTF-8"
		return m_response
		
class SynchorAPI(Resource):
	def get(self,id): 
		print("触发同步通知")
		if id == 'otc':
			id='6'
		gateway = GatewaytFactory.getPaymentGateway(int(id))
		m_res = gateway.synchor()
		#m_response = make_response(m_res)
		#m_response.headers["Content-type"]="text/html;charset=UTF-8"
		url = 'http://172.104.79.32/index.php/newlogic/paysuccess?orderid=%s&amount=%s&msg=%s&code=%s'%(m_res['orderid'],m_res['amount'],m_res['msg'],m_res['code'])
		return redirect(url, 302, Response)
		#return redirect(location, code, Response)
		
	def post(self,id):
		print("触发同步通知")
		if id == 'otc':
			id='6'
		gateway = GatewaytFactory.getPaymentGateway(int(id))
		m_res = gateway.synchor()
		#m_response = make_response(m_res)
		#m_response.headers["Content-type"]="text/html;charset=UTF-8"
		url = 'http://172.104.79.32/index.php/newlogic/paysuccess?orderid=%s&amount=%s&msg=%s&code=%s'%(m_res['orderid'],m_res['amount'],m_res['msg'],m_res['code'])
		return redirect(url, 302, Response)
		#return redirect(location, code, Response)


class NotifyAPI(Resource):
	def get(self,id):
		print("触发异步通知")
		resStr = ""
		try:
			if id == 'otc':
				id='6'
			Getway = GatewaytFactory.getPaymentGateway(int(id))
			Getway.notify()
			resStr = Getway.makeResponse()
		except BaseException as e:
			paylogger.error("异步通知解析错误-----------")
			paylogger.exception(e)
		m_response = make_response(resStr)
		m_response.headers["Content-type"]="text/html;charset=UTF-8"
		return m_response
			
	def post(self,id):
		print("触发异步通知")
		resStr = ""
		if id == 'otc':
			id='6'
		Getway = GatewaytFactory.getPaymentGateway(int(id))
		try:
			Getway.notify()
		except BaseException as e:
			paylogger.error("异步通知解析错误-----------")
			paylogger.exception(e)
		resStr = Getway.makeResponse()
		m_response = make_response(resStr)
		m_response.headers["Content-type"]="text/html;charset=UTF-8"
		return m_response

class MemberRecharge(Resource):
	from app.auth.common import token_auth
	decorators = [token_auth.login_required]
	def post(self,id):
		parser = RequestParser(trim=True)
		parser.add_argument('amount', type=float)
		parser.add_argument('remitter', type=str)
		parser.add_argument('msg', type=str)
		parser.add_argument('income_type', type=int)
		parser.add_argument('pay_type', type=int)
		parser.add_argument('bankId', type=int)
		parser.add_argument('accountName', type=int)
		m_args = parser.parse_args(strict=True)
		if not hasattr(g, 'current_member'):
			return {'errorCode': "9999",'errorMsg':"用戶未登录",'success': False}
		paylogger.info("%s用户公司入款 args:%s"%(g.current_member.username,m_args))
		uid = g.current_member.id
		member = Member.query.filter(Member.id == uid).first()
		status = member.status
		if status == 2:
			return {
				'errorCode': "9999",
				'errorMsg': "该用户已被冻结",
				'success': False
			}
		if status == 0:
			return {
				'errorCode': "9999",
				'errorMsg': "该用户已被禁用",
				'success': False
			}
		if m_args['amount'] == None or m_args['pay_type'] == None :
			return {"success":False, 'errorCode': "1010", 'errorMsg': "充值失败"}
		m_amount = m_args['amount']
		if m_amount <= 0:
			return {"success":False, 'errorCode': "1010", 'errorMsg': "充值失败，充值金额不正确"}
		ip = utils.host_to_value(request.remote_addr)
		m_res = Payment().recharge(id,m_args,g.current_member.id,g.current_member.username,ip)
		if m_res:
			return {"success":True}
		else:
			return {"success":False,'errorCode': "1010", 'errorMsg': "充值失败"}
