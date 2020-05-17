import json,hashlib,requests
from flask import request, g, current_app
import time
import base64
from pyDes import *
import binascii
from app.models.member_account_change import MemberAccountChangeRecord, Deposit
from .abstractGateway import AbstractGateway
import json,hashlib,requests
from flask_restful.reqparse import RequestParser
from flask import make_response
from app.models.memeber_history import OperationHistory
from app.gateway.gsrkGW import GsrkGW
from app.models import db
from app.common.utils import time_to_value,value_to_time,host_to_value


class BibaoGW(AbstractGateway):
    loginURL = '/coin/Login'
    getAddressURL = '/coin/GetAddress'
    addUserURL = '/coin/AddUser'
    orderDetail = '/coin/OrderDetail'  
    # 用户支付
    def toPay(self):
        m_res = self.AddUser()
        if not m_res['success']:
            return {'success':'False','errorMsg':'支付网关错误','errocode':'1044'}
        m_res = self.GetAddress()
        if not m_res['success']:
            return {'success':'False','errorMsg':'支付网关错误','errocode':'1044'}
        m_dataMap = {};
        # key A B C
        keyB = self.context['secret_key']
        keyA = keyB[0:6]
        keyC = keyB[6:]
        # 支付路由
        payUrl = (self.context['pay_url']+"/%s"+self.loginURL)%(self.context['code'])
        # 商户号
        MerCode = self.context['code']
        # 时间戳
        Timestamps = int(time.time())
        localTime = time.localtime(Timestamps)
        # 精确到天
        Timestamp = int(time.strftime("%Y%m%d", localTime))
        # 会员名称
        UserName = self.context["username"]
        # 请求类
        Type = 1
        # 币种
        Coin = 'DC'
        # 卖/买币数量,如果指定，则资金托管将根据数量进行限定
        Amount = self.context['amount']
        # 商户定义的唯一订单编号,长度不超过 32 位，数字货币交易订单变动通知，以 OrderNum 为准。
        OrderNum = self.context['orderid']
        # 商户限制的支付方式
        PayMethods = json.loads(self.context['pay_type_relation'])[str(self.context['pay_type'])]
        # DES加密算法
        m_arg = '''MerCode=%s&Timestamp=%s&UserName=%s&Type=%s&Coin=%s&Amount=%s&OrderNum=%s&PayMethods=%s''' % (
        MerCode, Timestamps, UserName, str(Type), Coin, Amount, OrderNum, PayMethods)
        secret_key = "bfGtSOFs"
        iv = secret_key
        k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(m_arg)
        # bytes.decode(en)
        # str(en, encoding="utf-8")
        # m = en.decode()
        m = binascii.b2a_hex(en)
        m = bytes.decode(m)
        # MD5加密算法
        m_param = MerCode + UserName + str(Type) + OrderNum + keyB + str(Timestamp)
        md = hashlib.md5()
        md.update((m_param).encode())
        m_sign = md.hexdigest()
        key = keyA + m_sign + keyC
        data = {"param": m, "Key": m_sign}
        header = {"Content-Type": "text/plain"}
        response = requests.get(payUrl + "?param=%s&Key=%s" % (m, key))
        m_res = response.text
        print('*******************************获取回调Token**************************************')
        print(m_res)
        print('*******************************获取回调Token**************************************')
        m_res = json.loads(m_res)
        if m_res['Success'] == 'False':
            return self.createErrorHtml(m_res['Message'])
        m_response = m_res['Data']['Url'] + '/' + m_res['Data']['Token']
        m_data = {'pay_url':m_response}
        return self.createHtml(m_data)

    # 返回一个html
    def createHtml(self,data):
        m_html = '''
            <body>
            <script type="text/javascript">
                window.location.href="%s";
            </script>
            </body>
            '''%(data['pay_url'])
        return m_html

    # 数字货币交易订单变动通知
    def getNotifyRequestParameter(self):
        parser = RequestParser()
        parser.add_argument('UserName',type=str)
        parser.add_argument('OrderId', type=str)
        parser.add_argument('OrderNum', type=str)
        parser.add_argument('Type', type=int)
        parser.add_argument('Coin', type=str)
        parser.add_argument('CoinAmount', type=str)
        parser.add_argument('LegalAmount', type=str)
        parser.add_argument('State1', type=int)
        parser.add_argument('State2', type=int)
        parser.add_argument('CreateTime', type=str)
        parser.add_argument('FinishTime', type=str)
        parser.add_argument('Remark', type=str)
        parser.add_argument('Price', type=str)
        parser.add_argument('Token', type=str)
        parser.add_argument('Sign', type=str)
        return parser.parse_args(strict=True)

    # 用户平台虚拟币余额查询
    def getOtcQuery(self):
        parser = RequestParser()
        parser.add_argument('UserName', type=str)
        parser.add_argument('OrderNum', type=str)
        parser.add_argument('Coin', type=str)
        parser.add_argument('Sign', type=str)
        return parser.parse_args(strict=True)

    # 获取银行卡信息
    def GetBankCard(self):
        parser = RequestParser()
        parser.add_argument('UserName', type=str)
        parser.add_argument('OrderNum', type=str)
        parser.add_argument('Sign', type=str)
        return parser.parse_args(strict=True)

    def validate(self, parser):
        # 按文档的要求拼拼接符串
        m_str = '''CreateTime=%s&Coin=%s&CoinAmount=%s&LegalAmount=%s&OrderId=%s&OrderNum=%s&Price=%s&Remark=%s&State1=%s&State2=%s&Token=%s&Type=%s&UserName=%s''' % (
        parser['CreateTime'], parser['Coin'], parser['CoinAmount'], parser['LegalAmount'], parser['OrderId'],
        parser['OrderNum'], parser['Price'], parser['Remark'], parser['State1'], parser['State2'], parser['Token'],
        parser['Type'], parser['UserName'])
        #生成加密数据
        m_sign = self.getSign(m_str, parser['OrderNum'], True)
        print('**********************************加密数据*************************************')
        print(m_sign)
        print('***********************************加密数据************************************')
        self.orderid = parser['OrderNum']
        self.amount = float(parser['CoinAmount'])
        self.porderid = parser['OrderNum']
        if parser['Sign'] == m_sign and parser['State1'] == 2 and parser['State2'] == 2:
            deposit = Deposit.query.filter(Deposit.number == parser['OrderNum']).first()
            mid = OperationHistory().getMemberAll(deposit.memberId)
            if mid.status == 2:
                return {"success": False, "errorMsg": "该用户已被冻结"}
            GW = GsrkGW()
            h_GW = GW.setContext(parser['OrderNum'])
            GW.orderid = parser['OrderNum']
            if deposit.pOrderid:
                GW.porderid = deposit.pOrderid
            else:
                GW.porderid = parser['OrderNum']
            GW.amount = parser['CoinAmount']
            try:
                if parser['State1'] == 2:
                    h_sign = GW.accountChange(100004, 0, 0)
                    if h_sign:
                        OperationHistory().PublicData(100004, deposit)
                        return {'messages': '充值成功', 'success': True}
                    else:
                        return {'errorMsg': '充值失败', 'success': False}
                else:
                    deposit = Deposit.query.filter(Deposit.number == parser['OrderNum']).first()
                    deposit_status = deposit.status
                    if deposit_status != 1:
                        return {'errorMsg': '状态错误', 'success': False}
                    else:
                        deposit.auditUser = g.current_user.id
                        deposit.auditTime = time_to_value()
                        deposit.auditHost = host_to_value(request.remote_addr)
                        deposit.status = parser['State1']
                db.session.add(deposit)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.remove()
        else:
            return False;


    # 添加用户
    def AddUser(self):
        m_dataMap = {};
        # key A B C
        keyB = self.context['secret_key']
        keyA = keyB[0:6]
        keyC = keyB[6:]
        # 商户号
        MerCode = self.context['code']
        # 支付路由
        payUrl = (self.context['pay_url']+'/{}'+self.addUserURL).format(MerCode)
        # 时间戳
        # 时间戳
        Timestamps = int(time.time())
        localTime = time.localtime(Timestamps)
        # 精确到天
        Timestamp = int(time.strftime("%Y%m%d", localTime))

        # 会员名称
        UserName = self.context["username"]
        # Des算法加密
        m_arg = 'MerCode=%s&Timestamp=%s&UserName=%s' % (MerCode, Timestamps, UserName)
        secret_key = "bfGtSOFs"
        iv = secret_key
        k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(m_arg)
        # bytes.decode(en)
        # str(en, encoding="utf-8")
        # m = en.decode()
        m = binascii.b2a_hex(en)
        m = bytes.decode(m)
        #print(m, type(m))
        m_key = MerCode + UserName + keyB + str(Timestamp)
        md = hashlib.md5()
        md.update((m_key).encode())
        m_sign = md.hexdigest()
        # 最后的Key值
        key = keyA + m_sign + keyC
        # response  = requests.get(payUrl+"?param=%s&Key=%s"%(m,key))
        # print(response.text)
        url = payUrl
        payload = {'param': m, "Key": key}
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        m_res = r.text
        m_res = json.loads(m_res)
        if 'Success' in m_res and 'Code' in m_res:
            if m_res['Success'] == True and m_res['Code'] == 1:
                return {'success':True,'massages':'成功','errocode':'1'}
            else:
                return {'success':False,'errorMsg':'支付网关错误','errocode':'102'}
        else:
            return {'success': False, 'errorMsg': '支付网关错误', 'errocode': '102'}

    # 获取地址
    def GetAddress(self):
        m_dataMap = {};
        # key A B C
        keyB = self.context['secret_key']
        keyA = keyB[0:6]
        keyC = keyB[6:]
        # 商户号
        MerCode = self.context['code']
        # 支付路由
        payUrl = (self.context['pay_url']+'/{}'+self.getAddressURL).format(MerCode)
        # 时间戳
        Timestamps = int(time.time())
        localTime = time.localtime(Timestamps)
        # 精确到天
        Timestamp = int(time.strftime("%Y%m%d", localTime))
        # 类型：1 会员，2 商户
        UserType = 1
        # 会员名称
        UserName = self.context['username']
        # 币种代码
        CoinCode = 'DC'
        # Key值的运算
        m_key = MerCode + str(UserType) + CoinCode + keyB + str(Timestamp)
        # md5加密算法
        md = hashlib.md5()
        md.update((m_key).encode())
        m_sign = md.hexdigest()
        # 最后的Key值
        key = keyA + m_sign + keyC

        # Des算法加密
        m_arg = 'MerCode=%s&Timestamp=%s&UserType=%s&UserName=%s&CoinCode=%s' % (
        MerCode, Timestamps, UserType, UserName, CoinCode)
        secret_key = "bfGtSOFs"
        iv = secret_key
        k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(m_arg)
        m = binascii.b2a_hex(en)
        m = bytes.decode(m)

        response = requests.get(payUrl + "?param=%s&Key=%s" % (m, key))
        m_res = response.text
        m_res = json.loads(m_res)
        if 'Success' in m_res and 'Code' in m_res:
            if m_res['Success'] == True and m_res['Code'] == 1:
                return {'success':True,'massages':'成功','errocode':'1'}
            else:
                return {'success':False,'errorMsg':'支付网关错误','errocode':'102'}
        else:
            return {'success': False, 'errorMsg': '支付网关错误', 'errocode': '102'}

    # 获取订单详情
    def OrderDetail(self):
        m_dataMap = {};
        # key A B C
        keyB = self.context['secret_key']
        keyA = keyB[0:6]
        keyC = keyB[6:]
        # 商户号
        MerCode = self.context['code']
        # 支付路由
        payUrl = 'http://opoutox.gosafepp.com/api/{}/coin/OrderDetail'.format(MerCode)
        # 时间戳
        Timestamps = int(time.time())
        localTime = time.localtime(Timestamps)
        # 精确到天
        Timestamp = time.strftime("%Y%m%d", localTime)
        # 会员名称
        UserName = 'zz123'
        # 平台商户订单号
        OrderNum = '1651652131'
        # Des算法加密
        m_arg = 'MerCode=%s&Timestamp=%s&UserName=%s&OrderNum=%s' % (MerCode, Timestamps, UserName, OrderNum)
        secret_key = "bfGtSOFs"
        iv = secret_key
        k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(m_arg)
        m = binascii.b2a_hex(en)
        m = bytes.decode(m)
        # Key值的运算
        m_key = MerCode + UserName + OrderNum + keyB + Timestamp
        # md5加密算法
        md = hashlib.md5()
        md.update((m_key).encode())
        m_sign = md.hexdigest()
        # 最后的Key值
        key = keyA + m_sign + keyC
        print(m_sign)
        print(key)
        response = requests.get(payUrl + "?param=%s&Key=%s" % (m, key))
        print(response.text)

    # 获取余额
    def GetBalance(self):
        m_dataMap = {};
        # key A B C
        keyB = self.context['secret_key']
        keyA = keyB[0:6]
        keyC = keyB[6:]
        # 商户号
        MerCode = self.context['code']
        # 支付路由
        payUrl = 'http://opoutox.gosafepp.com/api/{}/coin/GetBalance'.format(MerCode)
        # 时间戳
        Timestamps = int(time.time())
        localTime = time.localtime(Timestamps)
        # 精确到天
        Timestamp = int(time.strftime("%Y%m%d", localTime))
        print(Timestamp, type(Timestamp))
        # 类型：1 会员，2 商户
        UserType = 1
        # 会员名称
        UserName = 'zz123'
        # Key值的运算
        m_key = MerCode + str(UserType) + keyB + str(Timestamp)
        # md5加密算法
        md = hashlib.md5()
        md.update((m_key).encode())
        m_sign = md.hexdigest()
        # 最后的Key值
        key = keyA + m_sign + keyC
        # Des算法加密
        m_arg = 'MerCode=%s&Timestamp=%s&UserType=%s&UserName=%s' % (MerCode, Timestamps, UserType, UserName)
        print(m_arg)
        secret_key = "bfGtSOFs"
        iv = secret_key
        k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(m_arg)
        m = binascii.b2a_hex(en)
        print(m)
        m = bytes.decode(m)
        print(m, type(m))
        response = requests.get(payUrl + "?param=%s&Key=%s" % (m, key))
        print(response.text)
    # 查询状态
    def QueryStatus(self):
        m_dataMap = {};
        # key A B C
        keyB = self.context['secret_key']
        keyA = keyB[0:6]
        keyC = keyB[6:]
        # 商户号
        MerCode = self.context['code']
        # 支付路由
        payUrl = 'http://opoutox.gosafepp.com/api/{}/coin/QueryStatus'.format(MerCode)
        # 时间戳 精确到天
        Timestamps = int(time.time())
        localTime = time.localtime(Timestamps)
        Timestamp = int(time.strftime("%Y%m%d", localTime))
        # 商户平台订单号
        OrderNo = '123456789123456'
        # Des算法加密
        m_arg = 'MerCode=%s&Timestamp=%s&OrderNo=%s' % (MerCode, Timestamps, OrderNo)
        print(m_arg)
        secret_key = "bfGtSOFs"
        iv = secret_key
        k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(m_arg)
        m = binascii.b2a_hex(en)
        print(m)
        m = bytes.decode(m)
        print(m, type(m))
        # Key值的运算
        m_key = MerCode + OrderNo + keyB + str(Timestamp)
        # md5加密算法
        md = hashlib.md5()
        md.update((m_key).encode())
        m_sign = md.hexdigest()
        # 最后的Key值
        key = keyA + m_sign + keyC
        response = requests.get(payUrl + "?param=%s&Key=%s" % (m, key))
        print(response.text)

    def makeResponse(self):
        return '{"Success":true,"Code":1,"Message":"交易完成" }'