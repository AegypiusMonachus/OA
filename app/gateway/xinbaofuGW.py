from .abstractGateway import AbstractGateway
import json,hashlib,requests
from flask_restful.reqparse import RequestParser
from flask import make_response
'''
信宝付网关
'''
class XinbaofuGW(AbstractGateway):
    '''
    网关支付接口
    返回一个html
    '''
    def toPay(self):
        m_dataMap = self.context['data'];
        m_relation =  json.loads(m_dataMap['pay_type_relation'])
        parter = m_dataMap['code']
        key = m_dataMap['secret_key']
        #异步地址
        callbackurl = m_dataMap['nodify_url']
        #同步地址
        hrefbackurl = m_dataMap['return_url']
        currentTime = m_dataMap['currentTime']
        orderid =  m_dataMap['orderid']
        type = m_relation[str(m_dataMap['pay_type'])]
        attach = "";
        if 'attach' in m_dataMap.keys():
            attach =  m_dataMap['attach']
        payUrl = m_dataMap['pay_url']
        value = str(m_dataMap['amount']);
        m_param = "parter=" + str(parter) + "&type=" + str(type) + "&value=" + value + "&orderid=" + orderid + "&callbackurl=" + callbackurl
        md = hashlib.md5()
        md.update((m_param + key).encode())
        m_sign = md.hexdigest()
        url = payUrl + "?parter="+str(parter)+"&type="+str(type)+"&value="+value+"&orderid="+orderid+"&callbackurl="+callbackurl+ "&hrefbackurl="+hrefbackurl+"&payerIp="+"127.0.0.1"+"&attach="+attach+"&sign="+m_sign
        print(url)
        response  = requests.get(url)
        status_code = response.status_code
        if status_code >= 400:
            self.context['scuess'] = False
        else:
            self.context['scuess'] = True
        self.context['url'] = url;
        return response.text
    
    def getRequestParameter(self):
        parser = RequestParser()
        parser.add_argument('orderid', type=int, location=['form', 'json','args'], required=False)
        parser.add_argument('opstate', type=int, location=['form', 'json','args'], required=False)
        parser.add_argument('ovalue', type=float, location=['form', 'json','args'], required=False)
        parser.add_argument('orderamt', type=float, location=['form', 'json','args'], required=False)
        parser.add_argument('sysorderid', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('completiontime', type=str, location=['form', 'json','args'], required=False,default=1)
        parser.add_argument('attach', type=str, location=['form', 'json','args'], required=False,default=30)
        parser.add_argument('msg', type=str, location=['form', 'json','args'], required=False,default=30)
        parser.add_argument('sign', type=str, location=['form', 'json','args'], required=False,default=30)
        parser.add_argument('sign', type=str, location=['form', 'json','args'], required=False,default=30)
        
        return parser.parse_args(strict=True)

    def synchor(self): 
        parser = self.getRequestParameter()
        m_str = 'orderid=' + str(parser['orderid']) + '&opstate=' + str(parser['opstate']) + '&ovalue=' + str(parser['ovalue'])
        m_sign = self.getSign(m_str, parser['orderid'], True)
        m_args = {}
        m_args['pOrderid'] = parser['sysorderid']
        m_args['msg'] = parser['msg']
        self.updateRecharge(parser['orderid'], m_args)
        m_result={}
        m_result['orderid'] = parser['orderid'];
        m_result['amount'] = parser['ovalue'];
        if parser['opstate'] != 0:
            if parser['sign'] == m_sign:
                m_result['msg'] = '支付成功'
                m_result['code'] = 1
            else:
                m_result['msg'] = '支付失败'
                m_result['code'] = 0
        else:
            m_result['msg'] = '支付失败'
            m_result['code'] = 0
        return m_result
    
    def notify(self):   
        parser = self.getRequestParameter()
        m_str = 'orderid=' + str(parser['orderid']) + '&opstate=' + str(parser['opstate']) + '&ovalue=' + str(parser['ovalue'])
        m_sign = self.getSign(m_str, parser['orderid'], True)
        self.oderid = parser['orderid']
        self.amount = parser['ovalue']
        m_args = {}
        if parser['opstate'] != 0:
            m_args['msg'] = parser['msg']
            self.updateRecharge(parser['orderid'], m_args)
        if parser['sign'] == m_sign:
            self.accountChange(100004)
        m_response = make_response('ok')
        m_response.headers["Content-type"]="text/html;charset=UTF-8"
        return m_response