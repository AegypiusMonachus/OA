from .abstractGateway import AbstractGateway
import json,hashlib,requests
from flask_restful.reqparse import RequestParser
from flask import make_response
import time
'''
信宝付网关
'''
class Ryun70GW(AbstractGateway):
    '''
    网关支付接口
    返回一个html
    '''
    def toPay(self):
        m_dataMap = {};
        merchant = self.context['code']#商户号
        key = self.context['secret_key']
        #异步地址
        callbackurl = self.context['nodify_url']
        #同步地址
        hrefbackurl = self.context['return_url']
        currentTime = self.context['currentTime']
        localTime = time.localtime(currentTime) 
        strTime = time.strftime("%Y%m%d%H%M%S", localTime)
        orderid =  self.context['orderid']
        m_relation =  json.loads(self.context['pay_type_relation'])
        #type = m_relation[str(m_dataMap['pay_type'])]
        type = self.findPayType(self.context)
        remark =  None
        payUrl = self.context['pay_url']
        m_amount = self.context['amount']*100
        amount = str('%.2f' %m_amount);
        m_param = '''app_id=%s&notify_url=%s&out_trade_no=%s&total_amount=%s&trade_type=%s'''%(merchant,callbackurl,orderid,amount,type+key)
        print(m_param)
        md = hashlib.md5()
        md.update((m_param).encode())
        m_sign = md.hexdigest()
        m_data = {'app_id':merchant,'trade_type':type,'total_amount':amount,'out_trade_no':orderid,'notify_url':callbackurl,'interface_version':"V2.0",'return_url':hrefbackurl,'sign':m_sign}
        return self.createHtml(m_data,payUrl)
    
    def createHtml(self,data,payUrl):
        m_html = '''
            <body>
            <form id="pay_form" action="%s" method="post">
            <input type="hidden" name="app_id" value="%s">
            <input type="hidden" name="trade_type" value="%s">
            <input type="hidden" name="total_amount" value="%s">
            <input type="hidden" name="out_trade_no" value="%s">
            <input type="hidden" name="notify_url" value="%s">
            <input type="hidden" name="interface_version" value="%s">
            <input type="hidden" name="return_url" value="%s">
            <input type="hidden" name="sign" value="%s">
            </form>
            <script type="text/javascript">
                var form = document.getElementById('pay_form');
                form.submit();
            </script>
            </body>
            '''%(payUrl,data['app_id'],data['trade_type'],data['total_amount'],data['out_trade_no'],data['notify_url'],data['interface_version'],data['return_url'],data['sign'])
        return m_html
    def getNotifyRequestParameter(self):
        parser = RequestParser()
        parser.add_argument('total_amount', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('out_trade_no', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('trade_status', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('trade_no', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('extra_return_param', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('trade_time', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('sign', type=str, location=['form', 'json','args'], required=False)
        return parser.parse_args(strict=True)
        
    def synchor(self): 
        parser = self.getRequestParameter()
        print("同步通知传入参数%s"%(parser))
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
        m_str = '''out_trade_no=%s&total_amount=%s&trade_status=%s'''%(parser['out_trade_no'],parser['total_amount'],parser['trade_status'])
        #生成加密数据
        m_sign = self.getSign(m_str, parser['out_trade_no'], True)
        self.orderid = parser['out_trade_no']
        self.amount = float(parser['total_amount'])/100
        self.porderid = parser['trade_no']
        if parser['trade_status'] == 'SUCCESS' and parser['sign'] == m_sign:
            return True
        else:
            return False;
        
        
        