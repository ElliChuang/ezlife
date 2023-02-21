from mysql.connector import errorcode
import mysql.connector 
import redis
from config import MYSQL_USER, MYSQL_PW, MYSQL_HOST, REDIS_HOST


class MySQL():
    def conn_obj():
        dbconfig = {
            "user" : MYSQL_USER,
            "password" : MYSQL_PW,
            "host" : MYSQL_HOST,
            "database" : "ezlife",
        }
        conn_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = "ezlife_pool",
            pool_size = 10,
            pool_reset_session = True,
            **dbconfig)
        conn_obj = conn_pool.get_connection()

        return conn_obj



class Redis():
    def connect_to_redis():
        conn_redis = redis.Redis(host = REDIS_HOST, port = 6379)
        return conn_redis


