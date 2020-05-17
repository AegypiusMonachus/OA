'''
Created on 2018
推广链接
@author: liuyu
'''
from flask import abort
from .. import api
from app.models.blast_links import BlastLinks,LinksUser
from flask_restful import Resource, marshal_with
from app.models import db
from app.models.member import Member
import time
from ..common.utils import make_marshal_fields
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
from ..common.utils import *


'''
推广链接设置
'''
class LinksAPI(Resource):
    fields = make_marshal_fields({
        'lid': fields.Integer,
        'enable': fields.Integer,
        'uid':fields.Integer,
        'type':fields.Integer,
        'fanDian': fields.Integer,
        'link': fields.String,
    })
    @marshal_with(fields)
    def get(self, id=None):
        parser = RequestParser(trim=True)
        parser.add_argument('uid', type=str)
        args = parser.parse_args(strict=True) 
        criterion = set()
        if args['uid'] is not None:
            criterion.add(BlastLinks.uid == args['uid'])
        if id is not None:
            criterion.add(BlastLinks.lid == id)
        page = BlastLinks().getData(criterion)
        if page is None:
            return {
                'data': [],
                'success': True,
            }
        if not page.items:
            return None
        return {
            'success': True,
            'data': page.items,
            'pages': page.pages,
            'page': page.page,
            'pageSize': len(page.items)
        }
    
    '''
    '''
    def put(self, id=None):
        parser = RequestParser(trim=True)
        parser.add_argument('memberId', type=str)
        parser.add_argument('fanDian', type=float)
        parser.add_argument('enable', type=int)
        kwargs = parser.parse_args(strict=True)
        if id:
            kwargs = {key: value for key, value in kwargs.items() if value is not None}
            if kwargs['memberId'] is None:
                return make_response(error_code=400, error_message="缺少代理ID")
            if kwargs['fanDian']:
                daili = Member.query.filter(Member.id == kwargs['memberId']).first()
                if not daili or not daili.type:
                    return make_response(error_code=400, error_message="该代理不存在,无法修改")
                m_boolean = kwargs['fanDian'] <= daili.rebateRate or kwargs['fanDian'] == 0
                if not m_boolean:
                    return make_response(error_code=400, error_message="返点率不能超过" + str(float(daili.rebateRate)) + "%")
            kwargs.pop('memberId')
            m_result = BlastLinks().update(id,kwargs)
            return { 'success': True } 
        else:
            if kwargs['memberId']:
                for member_id in kwargs.pop('memberId').split(','):
                    links = BlastLinks.query.filter(BlastLinks.uid == member_id)
                    kwargs['enable'] = 0
                    for link in links:
                        for k, v in kwargs.items():
                            if v is not None:
                                if hasattr(link, k):
                                    setattr(link, k, v)
                        db.session.add(link)
                try:
                    db.session.commit()
                    return {'success': True}
                except:
                    db.session.rollback()
                    db.session.remove()
                    abort(500)
    '''
    '''
    @marshal_with(fields)
    def post(self):
        parser = RequestParser(trim=True)
        parser.add_argument('fanDian', type=float)
        parser.add_argument('uid', type=int)
        kwargs = parser.parse_args(strict=True)
        if kwargs['uid'] is not None:
            m_member = Member.query.filter(Member.id == kwargs['uid']).first()
            if m_member is None:
                abort(404)
            if kwargs['fanDian'] > m_member.rebateRate:
                abort(http_status_code=500,**{"success":False, 'errorCode': "2012", 'errorMsg': "返点要小于等于%s"%(m_member.rebateRate)})
            kwargs['type'] = 0
            kwargs['regIP'] = m_member.registrationHost
            kwargs['regTime'] = m_member.registrationTime
            kwargs['updateTime'] = int(time.time())
            kwargs['enable'] = 1
            kwargs['uid'] = m_member.id
        else:
            abort(404)
        m_result = BlastLinks().insert(**kwargs)
        return { 'data': [m_result],'success': True }
    
    def delete(self, id):
        m_res = BlastLinks().delete(id)
        return {'success': True}, 201 
    


'''
用户自定义推广链接
'''
class UserLinksAPI(Resource):
    fields = make_marshal_fields({
        'lid': fields.Integer,
        'enable': fields.Integer,
        'uid':fields.Integer,
        'fanDian': fields.Integer,
        'domain': fields.String,
        'web_domain': fields.String,
        'mobile_domain': fields.String,
    })
    @marshal_with(fields)
    def get(self, id=None):
        parser = RequestParser(trim=True)
        parser.add_argument('uid', type=str)
        args = parser.parse_args(strict=True) 
        criterion = set()
        if args['uid'] is not None:
            criterion.add(LinksUser.uid == args['uid'])
        if id is not None:
            criterion.add(LinksUser.lid == id)
        page = LinksUser().getData(criterion)
        if page is None:
            return {
                'success': True,
                'data': []
            }
        if not page.items:
            return None
        return {
            'data': page.items,
            'pages': page.pages,
            'page': page.page,
            'pageSize': len(page.items),
            'success': True
        }
    
    '''
    '''
    def put(self, id):
        parser = RequestParser(trim=True)
        parser.add_argument('fanDian', type=float)
        parser.add_argument('enable', type=int)
        parser.add_argument('domain', type=str)
        parser.add_argument('web_domain', type=str)
        parser.add_argument('mobile_domain', type=str)
        kwargs = parser.parse_args(strict=True)
        m_result = LinksUser().update(id,kwargs)
        return { 'success': True }
    '''
    '''
    @marshal_with(fields)
    def post(self):
        parser = RequestParser(trim=True)
        parser.add_argument('fanDian', type=float)
        parser.add_argument('uid', type=int)
        parser.add_argument('enable', type=int)
        parser.add_argument('domain', type=str)
        parser.add_argument('web_domain', type=str)
        parser.add_argument('mobile_domain', type=str)
        kwargs = parser.parse_args(strict=True)
        if kwargs['uid'] is not None:
            m_member = Member.query.filter(Member.id == kwargs['uid']).first()
            if m_member is None:
                abort(404)
            if kwargs['fanDian'] > m_member.rebateRate:
                kwargs['fanDian'] = m_member.rebateRate
            kwargs['enable'] = 1
        else:
            abort(404)
        m_result = LinksUser().insert(**kwargs)
        return { 'data': [m_result],'success': True }
    
    def delete(self, id):
        m_res = LinksUser().delete(id)
        return {'success': True}, 201
