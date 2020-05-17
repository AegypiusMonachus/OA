from .abstractGateway import AbstractGateway
import json,hashlib
from flask_restful.reqparse import RequestParser
import time
from app.log import paylogger
'''
SAF付网关
'''
class SAFGW(AbstractGateway):
    '''
    网关支付接口
    返回一个html
    '''
    def toPay(self):
        m_dataMap = {};
        merchant = self.context['code']#商户号
        key = self.context['secret_key']
        #异步地址
        nodifyurl = self.context['nodify_url']
        #同步地址
        returnurl = self.context['return_url']
        currentTime = self.context['currentTime']
        localTime = time.localtime(currentTime) 
        strTime = time.strftime("%Y%m%d%H%M%S", localTime)
        orderid =  self.context['orderid']
        m_relation =  json.loads(self.context['pay_type_relation'])
        #type = m_relation[str(m_dataMap['pay_type'])]
        type = self.findPayType(self.context)
        payUrl = self.context['pay_url']
        m_amount = self.context['amount']
        amount = int(m_amount);
        m_param = '''money=%s&notify_url=%s&out_trade_no=%s&pid=%s&return_url=%s&type=%s'''%(amount,nodifyurl,orderid,merchant,returnurl,type)
        md = hashlib.md5()
        md.update((m_param+key).encode())
        m_sign = md.hexdigest()
        m_param += '&sign=%s'%(m_sign)
        m_data = {'pay_url':payUrl+"?"+m_param}
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

       
    def getRequestParameter(self):
        parser = RequestParser()
        parser.add_argument('money', type=int, location=['form', 'json','args'], required=False)
        parser.add_argument('out_trade_no', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('trade_status', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('trade_no', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('pid', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('type', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('sign', type=str, location=['form', 'json','args'], required=False)
        return parser.parse_args(strict=True)
        
    def getNotifyRequestParameter(self):
        parser = RequestParser()
        parser.add_argument('money', type=int, location=['form', 'json','args'], required=False)
        parser.add_argument('out_trade_no', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('trade_status', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('trade_no', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('pid', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('type', type=str, location=['form', 'json','args'], required=False)
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
        #按文档的要求拼拼接符串
        m_str = '''money=%s&out_trade_no=%s&pid=%s&trade_no=%s&trade_status=%s&type=%s'''%(parser['money'],parser['out_trade_no'],parser['pid'],parser['trade_no'],parser['trade_status'],parser['type'])
        #生成加密数据
        m_sign = self.getSign(m_str, parser['out_trade_no'], True)
        self.orderid = parser['out_trade_no']
        self.amount = int(parser['money'])
        self.porderid = parser['trade_no']
        if parser['trade_status'] == 'TRADE_SUCCESS' and parser['sign'] == m_sign:
            return True
        else:
            return False;
        