import os, datetime


class Config:
	SECRET_KEY = os.getenv('SECRET_KEY', default='1E7AB4FFF67A59726E6681C2E87F68F0')

	STATIC_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static')

	@staticmethod
	def init_app(app):
		from logging.handlers import TimedRotatingFileHandler
		handler = TimedRotatingFileHandler(filename='log/log', when='MIDNIGHT', backupCount=7, atTime=datetime.time(0, 0, 0, 0))

		from logging import Formatter
		handler.setFormatter(
			Formatter('%(asctime)s | %(levelname)s | %(filename)s | %(module)s | %(lineno)d | %(funcName)s | %(message)s')
		)

		from flask.logging import default_handler
		app.logger.removeHandler(default_handler)
		app.logger.addHandler(handler)


class DebuggingConfig(Config):
	REDIS_HOST = '127.0.0.1'
	REDIS_PORT = 6379
	REDIS_PASS = None
	REDIS_POOLSIZE = 10
	DEBUG = True

	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:aq1sw2de3@104.155.233.75:13333/xc_test'
	SQLALCHEMY_COMMIT_ON_TEATDOWN = True
	SQLALCHEMY_ECHO = True
	SQLALCHEMY_POOL_SIZE = 5
	SQLALCHEMY_POOL_TIMEOUT = 10
	SQLALCHEMY_POOL_RECYCLE = 7200
	SQLALCHEMY_MAX_OVERFLOW = 5
	JOBS = [  # 任务列表
		{  # 第一个任务
		    'id': 'TransactionDetailsJob',
			'func': 'app.entertainmentcity.transactionDetails:job_1',
			'args': (900,),
			'trigger': {
				'type': 'cron',
				'hour': 18,
				'minute': 19,
				'second': 10
			}
		}

	]


class TestingConfig(Config):

	TESTING = True

	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:aq1sw2de3@104.155.233.75:13333/xc_test'
	SQLALCHEMY_COMMIT_ON_TEATDOWN = True
	SQLALCHEMY_ECHO = True
	SQLALCHEMY_POOL_SIZE = 5
	SQLALCHEMY_POOL_TIMEOUT = 10
	SQLALCHEMY_POOL_RECYCLE = 7200
	SQLALCHEMY_MAX_OVERFLOW = 5


class ProductionConfig(Config):
	DEBUG = False
	TESTING = False

	SQLALCHEMY_DATABASE_URI = ''
	SQLALCHEMY_COMMIT_ON_TEATDOWN = True
	SQLALCHEMY_ECHO = False
	SQLALCHEMY_POOL_SIZE = 5
	SQLALCHEMY_POOL_TIMEOUT = 10
	SQLALCHEMY_POOL_RECYCLE = 7200
	SQLALCHEMY_MAX_OVERFLOW = 5


config = {
	'DEBUGGING': DebuggingConfig,
	'TESTING': TestingConfig,
	'PRODUCTION': ProductionConfig,
}
