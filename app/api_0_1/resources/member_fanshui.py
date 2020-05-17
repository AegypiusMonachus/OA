from flask_restful import Resource, marshal_with, fields
from app.models.member_fanshui_pc import MemberFanshuiPc
from flask_restful.reqparse import RequestParser
from ..common.utils import make_response, make_marshal_fields


class MemberFanshui(Resource):
    @marshal_with(make_marshal_fields({
        'fanshuiTime': fields.String,
        "amount": fields.Float,
        "users": fields.String,
        "actionTime": fields.Integer,
    }))
    def get(self):
        parser = RequestParser(trim=True)
        parser.add_argument('agents', type=str)
        parser.add_argument('startTime', type=str)
        parser.add_argument('endTime', type=str)
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('pageSize', type=int, default=30)
        args = parser.parse_args(strict=True)
        res = MemberFanshuiPc().getFanshuiStatistics(**args)
        return make_response(data=res[0], page=res[1], pages=res[2], total=res[3])


class MemberFanshuiDetail(Resource):
    @marshal_with(make_marshal_fields({
        'uid': fields.Integer,
        "username": fields.String,
        "fs": fields.String,
    }))
    def get(self):
        parser = RequestParser(trim=True)
        parser.add_argument('agents', type=str)
        parser.add_argument('startTime', type=str)
        parser.add_argument('endTime', type=str)
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('pageSize', type=int, default=30)
        args = parser.parse_args(strict=True)
        res = MemberFanshuiPc().getFanshuiDetail(**args)
        return make_response(data=res[0], page=res[1], pages=res[2], total=res[3])
