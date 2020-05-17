from flask_restful import Resource, marshal_with, fields,abort
from flask_restful.reqparse import RequestParser
from app.api_0_1.common.utils import make_response,make_marshal_fields,make_response_from_pagination
from app.models.config_countries import ConfigCountries
from app.models.config_system import ConfigSystem
from app.models.common.utils import paginate
import json
import re
import os
from app.models import db

'''
系统设置 - 国别阻挡
'''
fields = make_marshal_fields({
		'id': fields.Integer,
		'name': fields.String,
		'ename': fields.String,
		'code': fields.String,
        'state': fields.Integer
    })

class ConfigCountriesAPI(Resource):
    @marshal_with(fields)	
    def get(self):
        parser = RequestParser(trim=True)
        parser.add_argument('name', type=str)
        args = parser.parse_args(strict=True)
        criterion = set()
        if args['name']:
            criterion.add(ConfigCountries.name == args['name'])
        pagination = paginate(ConfigCountries.query,criterion, 1, 300)
        return make_response_from_pagination(pagination)

    def put(self):
        parser = RequestParser(trim=True)
        parser.add_argument('clist', type=str)
        args = parser.parse_args(strict=True) 
        '''
        m_json = [];
        if args['clist'] is not None and args['clist'] != "":
            m_json = json.loads(args['clist']);
        m_res = ConfigSystem.query.get(1);
        m_path = m_res.parameter
        m_file = open(m_path,'r+',encoding='UTF-8')
        m_new_text ='';
        m_append = True;
        m_pattern = '^(?=.*?map)(?=.*?geoip_country_code).+$'
        try:
            m_lines = m_file.readlines()
            for line in m_lines:
                if re.search(m_pattern,line) is not None:
                    m_append = False
                if m_append == False:
                    if re.search('[}]$',line) is not None:
                        m_append = True
                        m_new_text += "map $geoip_country_code $allowed_country {" + '\n' +"default yes;" +'\n'
                        for m_country in m_json:
                            m_new_text += m_country + " no;" +"\n"
                        m_new_text += "}" +"\n"
                        continue
                if m_append:
                    m_new_text += line;
            m_file.seek(0)
            m_file.truncate()
            m_file.write(m_new_text);
        finally:
            m_file.close()
        m_log = os.popen("nginx -t -c %s"%(m_path))
		if m_log.find('successful')>= 0:
			return {'success':True}
		else:
			return {'success':False}
        '''
        return {'success':True}

    def post(self):
        parser = RequestParser(trim=True)
        parser.add_argument('data', type=str)
        args = parser.parse_args(strict=True)
        m_args_res = args['data']
        m_args = json.loads(m_args_res)
        try:
            for args_res in m_args:
                args_res = {key: value for key, value in args_res.items() if value is not None}
                id = args_res['id']
                ConfigCountries.query.filter(ConfigCountries.id == id).update(args_res)
            db.session.commit()
            result = []
            get_all = ConfigCountries.query.all()
            for i in range(len(get_all)):
                get_dict = {}
                get_dict['id'] = get_all[i].id
                get_dict['name'] = get_all[i].name
                get_dict['ename'] = get_all[i].ename
                get_dict['code'] = get_all[i].code
                get_dict['state'] = get_all[i].state
                result.append(get_dict)

        except:
            db.session.rollback()
            db.session.remove()
            abort(500)
        return make_response(result)
        
        
        