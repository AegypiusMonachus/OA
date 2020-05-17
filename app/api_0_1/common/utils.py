def make_marshal_fields(data_fields, **kwargs):
	from flask_restful import fields
	result = {
		'success': fields.Boolean,
		'data': fields.List(fields.Nested(data_fields)),
		'page': fields.Integer,
		'pages': fields.Integer,
		'pageSize': fields.Integer,
		'total': fields.Integer,
		'errorCode': fields.Integer,
		'errorMsg': fields.String,
	}
	for key in kwargs.keys():
		if key not in result:
			result[key] = kwargs[key]
	return result

def make_response(data=None, page=None, pages=None, total=None, error_code=None, error_message=None, **kwargs):
	result = {
		'success': data is not None,
		'data': data,
		'page': page,
		'pages': pages,
		'pageSize': len(data) if data else None,
		'total': total,
		'errorCode': error_code,
		'errorMsg': error_message,
	}
	for key in kwargs.keys():
		if key not in result:
			result[key] = kwargs[key]
	return result 

def make_response_from_pagination(pagination, **kwargs):
	from flask_sqlalchemy import Pagination
	if not isinstance(pagination, Pagination):
		raise TypeError
	return make_response(data=pagination.items, page=pagination.page, pages=pagination.pages, total=pagination.total, **kwargs)

def convert_pagination(pagination):
	items = []
	for item in pagination.items:
		items.append(dict(zip(item.keys(), item)))
	pagination.items = items
	return pagination

def save(storage):
	from flask import current_app, url_for

	import os
	path = os.path.abspath(current_app.config['STATIC_FOLDER'])

	import hashlib
	filename = hashlib.md5(storage.stream).hexdigest() + os.path.splitext(storage.filename)[1]
	try:
		storage.stream.seek(0)
		filename = 'temp' + os.path.splitext(storage.filename)[1]
		storage.save(os.path.join(path, filename))
	except:
		pass
	return url_for('get_static_file', filename=filename)

def is_float(money):
    try:
        float(money)
        if str(money) in ['inf', 'infinity', 'INF', 'INFINITY', 'True', 'NAN', 'nan', 'False', '-inf', '-INF', '-INFINITY', '-infinity', 'NaN', 'Nan']:
            return False
        else:
            return True
    except:
        return False
