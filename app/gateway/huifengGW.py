from .abstractGateway import AbstractGateway
import json,base64,time,requests
from flask_restful.reqparse import RequestParser
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import MD5
import ast
from app.models.common.utils import db
from app.log import paylogger
'''
汇丰支付
'''
class HuifengGW(AbstractGateway):
    '''
    网关支付接口
    返回一个html
    '''
    def toPay(self):
        extraStr = self.context['extra']
        if extraStr:
            try:
                self.context.update(ast.literal_eval(extraStr))
            except Exception as e:
                paylogger.exception(e)
                paylogger.error("汇丰支付获取extra数据错误:%s"%(extraStr))
                return self.createErrorHtml()
        param = {}
        param['orgId'] = self.context['orgId']#位机构号
        param['account'] = self.context['code']#商户号
        param['tranTp'] = "0"#交易类型 T0填0，T1填1
        private_key = self.context['secret_key']
        #异步地址
        param['notifyUrl'] = self.context['nodify_url']
        currentTime = self.context['currentTime']
        localTime = time.localtime(currentTime)
        param['orgOrderNo'] =  self.context['orderid']
        type = str(self.findPayType(self.context))
        param['source'] = str(type)#付款方式
        payUrl = self.context['pay_url']
        m_amount = self.context['amount']*100
        param['amount'] = str('%.0f' %m_amount);
        keyList = sorted(param.keys(),reverse=False)
        paramStr = ''
        for key in keyList:
            if param[key]:
                paramStr += '%s=%s&'%(key,param[key])
        paramStr = paramStr[:-1]
        private_keyBytes = base64.b64decode(private_key)
        priKey = RSA.importKey(private_keyBytes)
        signer = PKCS1_v1_5.new(priKey)
        hash_obj = MD5.new(paramStr.encode('utf-8'))
        signature = base64.b64encode(signer.sign(hash_obj))
        signature = bytes.decode(signature)
        param['signature'] = signature
        m_headers = {'Content-Type':'application/json'}
        m_data = json.dumps(param)
        response  = requests.post(payUrl,data = m_data,headers = m_headers)
        paylogger.info('汇丰支付%s'%(m_data))
        if response.status_code >= 400:
            paylogger.error("汇丰支付错误:%s"%(response.text))
            return self.createErrorHtml("支付失败")
        resJson = json.loads(response.text)
        if resJson['respCode'] != "200":
            paylogger.error("汇丰支付错误:%s"%(response.text))
            return self.createErrorHtml("支付失败")
        return self.createHtml(None,resJson['qrcode'])

    def createHtml(self,data,payUrl):
        m_html = '''
            <body>
            <script type="text/javascript">
                window.location.href="%s";
            </script>
            </body>
            '''%(payUrl)
        return m_html

    def getNotifyRequestParameter(self):
        parser = RequestParser()
        parser.add_argument('amount', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('extra', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('orderDt', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('orderNo', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('orgOrderNo', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('body', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('orgId', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('paySt', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('fee', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('signature', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('subject', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('respMsg', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('description', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('account', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('respCode', type=str, location=['form', 'json','args'], required=False)
        return parser.parse_args(strict=True)

    def synchor(self):
        parser = self.getRequestParameter()
        paylogger.info("同步通知传入参数%s"%(parser))
        success = self.validate(parser)
        m_args = {}
        m_args['pOrderid'] = parser['trade_no']
        self.updateRecharge(parser['out_trade_no'], m_args)
        m_result={}
        m_result['orderid'] = parser['out_trade_no'];
        m_result['amount'] = parser['total_amount'];
        if success:
            m_result['msg'] = '支付成功'
            m_result['code'] = 1
        else:
            m_result['msg'] = '支付失败'
            m_result['code'] = 0
        return m_result

    def validate(self,parser):
        #按文档的要求拼拼接符串
        self.context = parser
        paramStr = ''
        signature = parser.pop('signature')
        orderid = parser['orgOrderNo']
        keyList = sorted(parser.keys(),reverse=False)
        for key in keyList:
            if parser[key] and parser[key]!='':
                paramStr += '%s=%s&'%(key,parser[key])
        paramStr = paramStr[:-1]
        #生成加密数据
        m_sign = self.getSign(paramStr, parser['orgOrderNo'], signature)
        self.orderid = parser['orgOrderNo']
        self.amount = float(parser['amount'])/100
        self.porderid = parser['orderNo']
        return m_sign

    def getSign(self,str,orderid,hasSign):
        sql = '''select extra from blast_sysadmin_online where id = (select mBankId from blast_member_recharge
                where rechargeId = '%s')'''%(orderid)
        extraStr = db.session.execute(sql).scalar()
        if not extraStr:
            return False
        extraMap = ast.literal_eval(extraStr)
        if extraMap['publicKey']:
            public_keyBytes = base64.b64decode(extraMap['publicKey'])
            pubKey = RSA.importKey(public_keyBytes)
            hash_obj = MD5.new(str.encode('utf-8'))
            print(hash_obj.hexdigest())
            verifier = PKCS1_v1_5.new(pubKey)
            return verifier.verify(hash_obj, base64.b64decode(hasSign))
        return False;

    def makeResponse(self):
        return '{"success":"true"}'
