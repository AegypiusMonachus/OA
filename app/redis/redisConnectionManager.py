from redis import StrictRedis
import redis

class redisConnectionManager:
    def __init__(self):
        self.redisImpl = None
        self.app = None
    def init_app(self, app, dbIndex):
        self.app = app
        pool = redis.ConnectionPool(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            password=app.config['REDIS_PASS'],
            max_connections=app.config['REDIS_POOLSIZE'],
            db=dbIndex,
            decode_responses=True
        )
        self.redisImpl = redis.StrictRedis(connection_pool=pool)
    def get_redisImpl(self):
        return self.redisImpl

CERedisManager = redisConnectionManager()
IPRedisManager = redisConnectionManager()