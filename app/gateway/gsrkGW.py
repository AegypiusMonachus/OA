from .abstractGateway import AbstractGateway
import json,hashlib,requests
from flask_restful.reqparse import RequestParser
from flask import make_response
'''
公司入款网关
'''
class GsrkGW(AbstractGateway):
    def nodity(self):
        return