import redis
import mysql.connector 
from config import REDIS_HOST, DB_CONFIG


class Redis():
    def connect_to_redis():
        conn_redis = redis.Redis(host = REDIS_HOST, port = 6379)
        return conn_redis


class MySQL():
    def conn_obj():
        conn_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = "ezlife_pool",
            pool_size = 10,
            pool_reset_session = True,
            **DB_CONFIG)
        conn_obj = conn_pool.get_connection()
        return conn_obj