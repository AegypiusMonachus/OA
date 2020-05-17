from flask.json import jsonify


from . import auth_blueprint


@auth_blueprint.errorhandler(400)
def bad_request(e):
	response = jsonify({
		'success': False,
		'errorCode': 400,
		'errorMsg': 'Bad request',
	})
	response.status_code = 400
	return response


@auth_blueprint.errorhandler(401)
def unauthorized(e):
	response = jsonify({
		'success': False,
		'errorCode': 401,
		'errorMsg': 'Unauthorized',
	})
	response.status_code = 401
	return response


@auth_blueprint.errorhandler(403)
def forbidden(e):
	response = jsonify({
		'success': False,
		'errorCode': 403,
		'errorMsg': 'Forbidden',
	})
	response.status_code = 403
	return response


@auth_blueprint.errorhandler(404)
def not_found(e):
	response = jsonify({'error': 'Not found'})
	response.status_code = 404
	return response


@auth_blueprint.errorhandler(405)
def method_not_allowed(e):
	response = jsonify({'error': 'Method not allowed'})
	response.status_code = 405
	return response


@auth_blueprint.errorhandler(500)
def internal_server_error(e):
	response = jsonify({'error': 'Internal server error'})
	response.status_code = 500
	return response
