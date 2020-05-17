from app.models.common.utils import db
from flask_restful import abort
from ..gateway import GatewaytFactory
from .bank_account import SystemBankAccount
from .member import Member
from .member_account_change import Deposit
from app.common.orderUtils import createOrderId
import time
import requests
from app.log import paylogger
from app.models.memeber_history import OperationHistory

class Payment():

	def pay(self,m_id,m_args,uid,username,ip,realIp):
		m_amount = m_args['amount']
		m_sql = '''select ol.id, ol.pay_url,ol.accounts_url,ol.nodify_url,ol.return_url,
				ol.pay_type_relation,so.secret_key,so.tb,so.min_amount,so.max_amount,so.code,
				so.pay_type,so.id bankid ,ol.name gwname, so.name,so.extra 
				from blast_sysadmin_online so,tb_bank_online_list ol 
				where so.bank_online_id = ol.id and so.id = %s and so.enable = 1 and ol.enable = 1 
			'''%(m_id)
		m_result = db.session.execute(m_sql).first()
		if m_result is None:
			paylogger.info("%s用户支付错误,没有找到对应的网关信息"%(username))
			abort(500)
		m_json = dict(m_result)
		m_json['amount'] = m_amount;
		m_bool = (m_json['min_amount'] is not None and m_amount < m_json['min_amount']) or (m_json['max_amount'] is not None and m_amount > m_json['max_amount'])
		if m_bool:
			paylogger.info("%s用户支付错误,支付金额错误"%(username))
			return ''' <body> <a>支付错误：%s</a> </body> '''%("支付金额错误")
		m_gid = m_json['id']
		currentTime= int(time.time());
		m_json['currentTime'] = currentTime
		m_json['orderid'] = createOrderId(0,uid,1,None)
		m_json['ip'] = ip
		m_json['realIp'] = realIp
		m_json["username"]=username
		m_json["bank_type"] = m_args["bank_type"]
		m_context =m_json
		#从静态工厂方法实例化具体的支付网关
		paylogger.info("%s用户支付%s使用%s支付方式"%(username,m_amount,m_json['name']))
		Gateway = GatewaytFactory.getPaymentGateway(m_gid)
		Gateway.setContext(m_context)
		try:
			m_res = Gateway.toPay()
			self.insert(m_id, uid, username, ip, m_json,100004)
			try:
				requests.request('GET', 'http://127.0.0.1:8125/main/memberOnlinePayment', timeout=1)
			except:
				pass
		except Exception as e:
			paylogger.exception(e)
			paylogger.error("%s用户支付%s错误"%(username,m_amount))
			abort(http_status_code=500,**{"success":False, 'errorCode': "1010", 'errorMsg': "充值错误"})
		return m_res
	
	def recharge(self,m_id,m_args,uid,username,ip):
		pay_type = m_args['pay_type']
		if pay_type == 2001:
			systemBankAccount = SystemBankAccount.query.filter(SystemBankAccount.id == m_id).first()
			if systemBankAccount is None:
				return {"success":False, 'errorCode': "1010", 'errorMsg': "充值失败"}
		currentTime= int(time.time());
		m_args['currentTime'] = currentTime
		m_args['orderid'] = createOrderId(0,uid,1,None)
		res =  self.insert(m_id, uid, username, ip, m_args,100003);
		try:
			requests.request('GET', 'http://127.0.0.1:8125/main/memberDeposit', timeout=1)
		except:
			pass
		return res;
	def insert(self,m_id,uid,username,ip,m_json,type):
		members = Member.query.filter(Member.username == username).first()
		try:
			deposit = Deposit()
			deposit.memberId = uid
			deposit.username = username
			deposit.systemBankAccountId = m_id
			deposit.number = int(m_json['orderid'])
			deposit.status = 1
			deposit.type = type
			deposit.applicationHost = ip
			deposit.applicationAmount = m_json['amount']
			deposit.applicationTime = m_json['currentTime']
			if type == 100004:
				deposit.auditTime = m_json['currentTime']
			if 'bankId' in m_json:
				deposit.bankAccountId = m_json['bankId']
			if 'remitter' in m_json:
				deposit.remitter = m_json['remitter']
			if 'msg' in m_json:
				deposit.msg = m_json['msg']
			if 'income_type' in m_json:
				deposit.income_type = m_json['income_type']
			deposit.pay_type = m_json['pay_type']
			deposit.isAcdemen = 1
			db.session.add(deposit)
			db.session.commit()
			OperationHistory().PublicMeDatasApply(type, deposit)
			return True;
		except Exception as e:
			db.session.rollback()
			db.session.remove()
			paylogger.error("%s用户公司入款错误 : "%(username,e))
			return False;
