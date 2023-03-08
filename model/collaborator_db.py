from mysql.connector import errorcode
import mysql.connector 
from config import DB_CONFIG


class CollaboratorModel():
    def __init__(self):
        self.conn_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = "ezlife_pool",
            pool_size = 10,
            pool_reset_session = True,
            **DB_CONFIG)


    def check_edit_permission(self, created_member_id, book_id):
        try:
            connection_object = self.conn_pool.get_connection()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        SELECT * FROM account_book 
                        WHERE created_member_id = %s AND id = %s
                    """)
            mycursor.execute(query, (created_member_id, book_id))
            result = mycursor.fetchone()
            if result:
                return "SUCCESS"
            else:
                return None
            
        except mysql.connector.Error as err:
            print("Something went wrong when check edit permission: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    def add_collaborator(self, collaborator_id, book_id):
        try:
            connection_object = self.conn_pool.get_connection()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        INSERT INTO collaborator (collaborator_id, book_id) 
                        VALUE (%s, %s) 
                        ON DUPLICATE KEY UPDATE collaborator_id = %s, book_id = %s
                    """)
            mycursor.execute(query, (collaborator_id, book_id, collaborator_id, book_id))
            rows_affected = mycursor.rowcount
            connection_object.commit() 
            if rows_affected:
                return "SUCCESS"
            else:
                return None
            
        except mysql.connector.Error as err:
            print("Something went wrong when adding collaborator: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

    
    def delete_collaborator(self, collaborator_id, book_id):
        try:
            connection_object = self.conn_pool.get_connection()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        DELETE c FROM collaborator c
                        WHERE c.collaborator_id = %s AND c.book_id = %s
                    """)
            mycursor.execute(query, (collaborator_id, book_id))
            rows_affected = mycursor.rowcount
            connection_object.commit() 
            if rows_affected:
                return "SUCCESS"
            else:
                return None
            
        except mysql.connector.Error as err:
            print("Something went wrong when deleting collaborator: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


collaboratorModel = CollaboratorModel()