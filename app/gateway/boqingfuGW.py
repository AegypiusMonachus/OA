from .abstractGateway import AbstractGateway
import json,hashlib,requests
from flask_restful.reqparse import RequestParser
from flask import make_response
import time
'''
信宝付网关
'''
class BoqingfuGW(AbstractGateway):
    '''
    网关支付接口
    返回一个html
    '''
    def toPay(self):
        m_dataMap = self.context['data'];
        m_relation =  json.loads(m_dataMap['pay_type_relation'])
        merchant = m_dataMap['code']#商户号
        key = m_dataMap['secret_key']
        #异步地址
        callbackurl = m_dataMap['nodify_url']
        #同步地址
        hrefbackurl = m_dataMap['return_url']
        currentTime = m_dataMap['currentTime']
        localTime = time.localtime(currentTime) 
        strTime = time.strftime("%Y%m%d%H%M%S", localTime)
        orderid =  m_dataMap['orderid']
        type = m_relation[str(m_dataMap['pay_type'])]
        remark =  None
        payUrl = m_dataMap['pay_url']
        amount = str('%.2f' %m_dataMap['amount']);
        m_param = '''amount=%s&currentTime=%s&merchant=%s&notifyUrl=%s&orderNo=%s&payType=%s'''%(amount,strTime,merchant,callbackurl,orderid,type)
        if remark is not None:
            m_param += '&remark=%s'%(remark)
        m_param += '&returnUrl=%s'%(hrefbackurl)
        m_param += '#'
        print(m_param)
        md = hashlib.md5()
        md.update((m_param + key).encode())
        m_sign = md.hexdigest()
        m_data = {'amount':amount,'currentTime':strTime,'merchant':merchant,'notifyUrl':callbackurl,'orderNo':orderid,'payType':type,'remark':remark,'returnUrl':hrefbackurl,'sign':m_sign}
        response  = requests.post(payUrl,m_data)
        status_code = response.status_code
        if status_code >= 400:
            self.context['scuess'] = False
        else:
            self.context['scuess'] = True
        return response.text
    
    def getRequestParameter(self):
        parser = RequestParser()
        parser.add_argument('accFlag', type=int, location=['form', 'json','args'], required=False)
        parser.add_argument('accName', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('amount', type=float, location=['form', 'json','args'], required=False)
        parser.add_argument('createTime', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('currentTime', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('merchant', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('orderNo', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('payFlag', type=int, location=['form', 'json','args'], required=False)
        parser.add_argument('payTime', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('payType', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('remark', type=str, location=['form', 'json','args'], required=False,default=30)
        parser.add_argument('systemNo', type=str, location=['form', 'json','args'], required=False)
        parser.add_argument('sign', type=str, location=['form', 'json','args'], required=False,default=30)
        return parser.parse_args(strict=True)

    def synchor(self): 
        parser = self.getRequestParameter()
        m_args = {}
        m_str = '''accFlag=%s&accName=%s&amount=%s&createTime=%s&currentTime=%s&merchant=%s&orderNo=%s&payFlag=%s&payTime=%s&payType=%s
        '''%(parser['accFlag'],parser['accName'],parser['amount'],parser['createTime'],parser['currentTime'],parser['merchant'],parser['orderNo'],parser['payFlag'],parser['payTime'],parser['payType'])
        if parser['remark']:
            m_str += '&remark=%s'%(parser['remark'])
            m_args['msg'] = parser['remark']
        m_str += '&systemNo=%s'%(parser['systemNo'])
        m_str += '#'
        m_sign = self.getSign(m_str, parser['orderNo'], True)
        m_args['pOrderid'] = parser['systemNo']
        self.updateRecharge(parser['orderNo'], m_args)
        m_result={}
        m_result['orderid'] = parser['orderNo'];
        m_result['amount'] = parser['amount'];
        if parser['payFlag'] != 2:
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
        m_args = {}
        m_str = '''accFlag=%s&accName=%s&amount=%s&createTime=%s&currentTime=%s&merchant=%s&orderNo=%s&payFlag=%s&payTime=%s&payType=%s
        '''%(parser['accFlag'],parser['accName'],parser['amount'],parser['createTime'],parser['currentTime'],parser['merchant'],parser['orderNo'],parser['payFlag'],parser['payTime'],parser['payType'])
        if parser['remark']:
            m_str += '&remark=%s'%(parser['remark'])
            m_args['msg'] = parser['remark']
        m_str += '&systemNo=%s'%(parser['systemNo'])
        m_str += '#'
        m_sign = self.getSign(m_str, parser['orderNo'], True)
        self.oderid = parser['orderNo']
        self.amount = parser['amount']
        if parser['payFlag'] == 2:
            if parser['sign'] == m_sign:
                self.accountChange(100004)
                m_response = make_response('success')
            else:
                m_response = make_response('success')
        else:
            m_response = make_response('success')
        m_response.headers["Content-type"]="text/html;charset=UTF-8"
        return m_response