def create_app(config_name):
    from flask import Flask
    app = Flask(__name__, static_url_path='/api/static')

    from flask_cors import CORS
    CORS(app)

    from config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    '''
	from .extensions import socketio, background_task
	socketio.init_app(app)
	socketio.start_background_task(background_task)
	'''

    from .models import db
    db.init_app(app)

    from app.redis.redisConnectionManager import (CERedisManager, IPRedisManager)
    CERedisManager.init_app(app, 15)
    IPRedisManager.init_app(app, 14)
    from app.models.config_iplist import ConfigIplist
    ConfigIplist.getDataToRedis()
    from app.entertainmentcity.transactionDetails import ecBetsDetailsToRedis
    import time
    ecBetsDetailsToRedis(int(time.time())-3600,int(time.time()))
    from app.schedule import scheduler
    scheduler.init_app(app)
    scheduler.start()

    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

    from .common import common_blueprint
    app.register_blueprint(common_blueprint, url_prefix='/api/common')

    from .api_0_1 import api_0_1_blueprint
    app.register_blueprint(api_0_1_blueprint, url_prefix='/api/0.1')

    from .disc import disc_blueprint
    app.register_blueprint(disc_blueprint, url_prefix='/api/disc')

    from .ec import ec_0_1_blueprint
    app.register_blueprint(ec_0_1_blueprint, url_prefix='/API')

    from .noauth import noauth_blueprint
    app.register_blueprint(noauth_blueprint, url_prefix='/api/other')

    '''
	@app.errorhandler(Exception)
	def error_handler(e):
		from flask import current_app
		current_app.logger.exception(e)
	'''

    @app.before_request
    def before_request():
        from flask_restful import request, abort
        from app.redis.redisConnectionManager import IPRedisManager
        from flask.json import jsonify
        ip = request.remote_addr  # 127.0.0.1
        # 查询redis, 如果有数据允许访问
#         with IPRedisManager.app.app_context():
#             redisImpl = IPRedisManager.get_redisImpl()
# 
#             if redisImpl.hexists("IPList", ip) == 0:
#                 return jsonify({
#                     'success': False,
#                     'errorCode': 403,
#                     'msg':'您没有权限访问！'
#                 })
    @app.after_request
    def after_request(response):
        response.status_code = 200
        return response

    @app.errorhandler(KeyError)
    def key_error_handler(error):
        app.logger.exception(error)

    from sqlalchemy.exc import SQLAlchemyError
    @app.errorhandler(SQLAlchemyError)
    def alchemy_error_handler(error):
        app.logger.exception(error)

    @app.route('/api/static/<filename>', methods=['GET'])
    def get_static_file(filename):
        from flask import request
        from flask.json import jsonify
        from app.auth.common import verify_token

        token = request.args.get('token')
        if not token:
            return jsonify({
                'success': False,
                'errorCode': 400,
            })
        if not verify_token(token):
            return jsonify({
                'success': False,
                'errorCode': 401
            })
        return app.send_static_file(filename)

    return app
