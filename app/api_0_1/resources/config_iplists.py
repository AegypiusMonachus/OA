from flask import request, g
from flask_restful import Resource, marshal_with, fields
from flask_restful.reqparse import RequestParser
from app.api_0_1.common.utils import make_marshal_fields,make_response,make_response_from_pagination
# from .. import api
from ..parsers.systemConfig import configIplist_parsers_post,configIplist_parsers_put
from app.models.config_iplist import ConfigIplist
from pickle import NONE
import json
import time
from flask.json import jsonify
from app.redis.redisConnectionManager import IPRedisManager

fields = make_marshal_fields({
        'id': fields.Integer,
        'ip': fields.String,
        'state': fields.Integer,
        'uid': fields.Integer,
        'strTime': fields.String
})

class ConfigIplistAPI(Resource):
    # 查询
    @marshal_with(fields)
    def get(self,id=None):
        m_args = configIplist_parsers_put.parse_args(strict=True)
        criterion = set()
        if id:
            criterion.add(ConfigIplist.id == id)
        m_result = ConfigIplist().getDate(criterion,m_args['page'],m_args['pageSize'])
        return make_response_from_pagination(m_result)


    # 添加
    @marshal_with(fields)
    def post(self):
        m_args = configIplist_parsers_post.parse_args(strict=True)
        # print(m_args['ip'])
        m_args['uid'] = g.current_user.id
        currentTime = int(time.time())
        localTime = time.localtime(currentTime)
        strTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
        m_args['strTime'] = strTime
        del m_args['page']
        del m_args['pageSize']

        # 不允许重复插入
        m_result = ConfigIplist().getIpToUpdate()
        ip_list = []
        for i in m_result:
            ip = i.ip
            ip_list.append(ip)

        if m_args['ip'] not in ip_list:
            m_res = ConfigIplist().insert(**m_args)
            redisImpl = IPRedisManager.get_redisImpl()
            redisImpl.hset(name="IPList", key=m_args['ip'], value="")
            return make_response(data=[m_res], page=1, pages=1, total=1, error_message='添加成功')
        else:
            return make_response(error_code=400, error_message='添加失败')

    # 更改
    @marshal_with(fields)
    def put(self, id):
        m_args = configIplist_parsers_put.parse_args(strict=True)
        m_args['uid'] = g.current_user.id
        del m_args['page']
        del m_args['pageSize']
        m_res = ConfigIplist().update(id, **m_args)
        return make_response(data=m_res,page=1, pages=1, total=1)

    # 删除
    def delete(self,id):
        m_result = ConfigIplist().getIpToDelete(id)
        m_res = ConfigIplist().delete(id)
        if m_result:
            with IPRedisManager.app.app_context():
                redisImpl = IPRedisManager.get_redisImpl()
                redisImpl.hdel("IPList", m_result.ip)
            return jsonify({
                'success': True,
                'Code': 201,
                'msg': '删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'Code': 404,
                'msg': '删除失败'
            })
