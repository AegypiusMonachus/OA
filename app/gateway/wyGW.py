from .abstractGateway import AbstractGateway
import json,hashlib
from flask_restful.reqparse import RequestParser
from app.log import paylogger
from datetime import datetime
import ast
import requests
'''
望远付网关
'''
class WyGW(AbstractGateway):
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
        type = self.findPayType(self.context)
        self.context['type'] = type
        payUrl = self.context['pay_url']
        mdata = self.createData()
        response  = requests.post(payUrl,data = mdata,headers = None)
        if response.status_code >= 400:
            paylogger.error("望远支付错误:%s"%(response.text))
            return self.createErrorHtml("支付失败")
        resJson = json.loads(response.text)
        if resJson['code'] != "E000":
            paylogger.error("望远支付错误:%s"%(response.text))
            return self.createErrorHtml("支付失败")
        self.orderid = self.context['orderid']
        self.porderid = resJson['net_bill_no']
        if resJson['net_bill_no']:
            self.updateRecharge()
        return self.createHtml(None,resJson['qrCode'])
        
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

    def getNotifyRequestParameter(self):
        parser = RequestParser()
        parser.add_argument('code', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('message', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('mch_id', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('net_bill_no', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('bill_id', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('pay_type', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('amount', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('receipt_amount', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('sign', type=str, location=['form', 'json','args'], required=False)
        return parser.parse_args(strict=True)
        
    def synchor(self): 
        parser = self.getRequestParameter()
        paylogger.info("同步通知传入参数%s"%(parser))
        success = self.validate(parser)
        self.updateRecharge()
        m_result={}
        m_result['orderid'] = parser['out_trade_no'];
        m_result['amount'] = parser['money'];
        if success:
            m_result['msg'] = '支付成功'
            m_result['code'] = 1
        else:
            m_result['msg'] = '支付失败' 
            m_result['code'] = 0
        return m_result
    
    def validate(self,parser):
        self.context = parser
        paramStr = ''
        signature = parser.pop('sign')
        orderid = parser['bill_id']
        keyList = sorted(parser.keys(),reverse=False)
        for key in keyList:
            if parser[key] and parser[key]!='':
                paramStr += '%s=%s&'%(key,parser[key])
        paramStr = paramStr[:-1]
        paramStr += '&&mch_key='
        #生成加密数据
        m_sign = self.getSign(paramStr, orderid, True)
        self.orderid = orderid
        self.amount = float(parser['amount'])
        self.porderid = parser['net_bill_no']
        if parser['code'] == '1' and signature == m_sign:
            return True
        else:
            return False;
    
    def createData(self):
        mdata = {}
        mdata['bill_id'] = self.context['orderid']
        mdata['goods_name'] = self.context['username']
        mdata['amount'] = float(self.context['amount'])
        mdata['goods_note'] = '一条裤子'
        mdata['mch_bill_time'] = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S') 
        mdata['notify_url'] = self.context['nodify_url']
        mdata['return_url'] = self.context['return_url']
        mdata['version'] = '2'
        mdata['mch_id'] = self.context['code']
        mdata['pay_type'] = self.context['type']
        mdata['mch_app'] = self.context['mch_app']
        mdata['user_ip'] = self.context['realIp']
        keyList = sorted(mdata.keys(),reverse=False)
        paramStr = ''
        for key in keyList:
            if mdata[key]:
                paramStr += '%s=%s&'%(key,mdata[key])
        paramStr = paramStr[:-1]
        paramStr += '&mch_key=' + self.context['secret_key']
        print(paramStr)
        md = hashlib.md5()
        md.update((paramStr).encode())
        m_sign = md.hexdigest()
        mdata['sign'] = m_sign
        return mdata
        