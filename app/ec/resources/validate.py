from flask_restful import Resource
from flask import request,make_response
'''
API认证
'''
class ValidateAPI(Resource):
    def post(self):
        m_str = request.data
        m_data = '''{"Guid": "80325e86-f6da-442d-ae3b-cf4411565ba4","Success": True,"Code": "0","Message": "Success","Data": null}'''
        m_response = make_response(m_data)
        m_response.headers["Content-type"]="text/plain"
        return m_response
