from mysql.connector import errorcode
import mysql.connector 
from config import MYSQL_PW, MYSQL_HOST


class MySQL():
    def conn_obj():
        dbconfig = {
            "user" : "admin",
            "password" : MYSQL_PW,
            "host" : MYSQL_HOST,
            "database" : "ezlife",
        }
        conn_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = "ezlife_pool",
            pool_size = 15,
            pool_reset_session = True,
            **dbconfig)
        conn_obj = conn_pool.get_connection()

        return conn_obj

