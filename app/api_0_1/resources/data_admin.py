'''
Created on 2018
预设开奖数据
@author: liuyu
'''
from flask_restful import Resource, marshal_with
from .. import api
from app.models.blast_type import BlastType
from app.models.blast_data_admin import BlastDataAdmin
from ..parsers.lotteryParsers import dataAdmin_get_parser,data_admin_post_parser
from flask_restful import fields
from app.api_0_1.common.utils import make_marshal_fields,make_response_from_pagination
'''
预设开奖数据
预设开奖数据优先级最大
id:彩票的ID，举例:河内五分彩的id=5
'''
#@api.resource('/dataadmin', '/dataadmin/<int:id>')
class DataAdminAPI(Resource):
    
    '''
    查询现在已经有的预设信息
    '''
    @marshal_with(make_marshal_fields({
        'id': fields.Integer,
        'type': fields.Integer,
        'time': fields.Integer,
        'actionNo' : fields.String,
        'data' : fields.String,
        'uid': fields.Integer,
        'username': fields.String,
        'actionTime': fields.String,
    }))
    def get(self):
        m_args = dataAdmin_get_parser.parse_args(strict=True)
        criterion = set()
        if m_args['sActionTime']:
            criterion.add(BlastDataAdmin.time >= m_args['sActionTime'])
        if m_args['eActionTime']:
            criterion.add(BlastDataAdmin.time <= m_args['eActionTime'])
        if m_args['username']:
            criterion.add(BlastDataAdmin.username == m_args['username'])
        if m_args['actionNo']:
            criterion.add(BlastDataAdmin.actionNo == m_args['actionNo'])
        if m_args['type']:
            criterion.add(BlastDataAdmin.type == m_args['type'])
        m_orm = BlastDataAdmin()
        pagination = m_orm.getBlastDataAdmin(criterion,m_args['page'],m_args['pageSize']);
        return make_response_from_pagination(pagination)
    
    '''
    更新一个系统开奖信息
    '''
    #@marshal_with(systemConfig_fields.basic_fields)
    def put(self,id):
        kwargs = data_admin_post_parser.parse_args(strict=True)
        m_result = BlastDataAdmin().update(id,kwargs)
        return m_result
    '''
    添加一个系统开奖信息
    '''
    @marshal_with({
        'data': fields.List(fields.Nested({
            'id': fields.Integer,
            'type': fields.Integer,
            'time': fields.Integer,
            'actionNo' : fields.String,
            'data' : fields.String,
            'uid': fields.Integer,
            'username': fields.String,
        })),
        'success': fields.Boolean(default=True),
        'pages': fields.Integer(default=1),
        'page': fields.Integer(default=1),
        'pageSize': fields.Integer(default=1),
    })
    def post(self,id):
        kwargs = data_admin_post_parser.parse_args(strict=True)
        kwargs['type'] = id
        m_result = BlastDataAdmin().insert(kwargs)
        return { 'data': [m_result] }
    
    #@marshal_with(systemConfig_fields.basic_fields)
    def delete(self, id):
        m_res = BlastDataAdmin().delete(id)
        return {'success': m_res}, 201 
    
#@api.resource('/rollback/<int:type>/<string:number>')
class DataRollBackAPI(Resource):
    #@marshal_with(systemConfig_fields.basic_fields)
    def post(self,type,number):
        m_result = BlastDataAdmin.rollBack(number,type)
        return { 'success': m_result }
    
