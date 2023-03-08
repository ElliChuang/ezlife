import redis
from config import REDIS_HOST


class Redis():
    def connect_to_redis():
        conn_redis = redis.Redis(host = REDIS_HOST, port = 6379)
        return conn_redis


