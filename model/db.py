from mysql.connector import errorcode
import mysql.connector 
from config import MySQL_PW


class MySQL():
    def conn_obj():
        dbconfig = {
            "user" : "root",
            "password" : MySQL_PW,
            "host" : "localhost",
            "database" : "ezlife",
        }
        conn_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = "taipei_pool",
            pool_size = 30,
            pool_reset_session = True,
            **dbconfig)
        conn_obj = conn_pool.get_connection()

        return conn_obj

