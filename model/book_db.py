from mysql.connector import errorcode
import mysql.connector
from model.db import MySQL 


class BookModel(): 
    def get_book_auth(book_id):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        SELECT m.id, m.name, b.book_name, m2.name as host_member FROM collaborator AS c
                        INNER JOIN member AS m ON m.id = c.collaborator_id
                        INNER JOIN account_book AS b ON c.book_id = b.id
                        INNER JOIN member AS m2 ON b.created_member_id = m2.id
                        WHERE c.book_id = %s 
                        ORDER BY m.name
                    """)
            mycursor.execute(query, (book_id,))
            results = mycursor.fetchall()
            if results:
                return results
            else:
                return None
            
        except mysql.connector.Error as err:
            print("Something went wrong when getting book auth: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    def get_books_by_member(member_id):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        SELECT 
                            b.id, 
                            b.book_name, 
                            b.created_member_id
                        FROM account_book AS b 
                        INNER JOIN collaborator as c ON b.id = c.book_id
                        WHERE c.collaborator_id = %s
                        GROUP BY b.id
                    """)
            mycursor.execute(query, (member_id,))
            results = mycursor.fetchall()
            if results:
                return results
            else:
                return None
            
        except mysql.connector.Error as err:
            print("Something went wrong when getting books: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    def check_if_exist(book_name, created_member_id):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        SELECT book_name FROM account_book 
                        WHERE book_name = %s AND created_member_id = %s
                    """)
            mycursor.execute(query, (book_name, created_member_id,))
            result = mycursor.fetchone()
            if result:
                return "ALREADY EXIST"
            else:
                return None
            
        except mysql.connector.Error as err:
            print("Something went wrong when checking if book exist: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

    
    def create_book(book_name, created_member_id):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            mycursor.execute("START TRANSACTION")
            query = ("""
                        INSERT INTO account_book (book_name, created_member_id)
                        VALUES (%s, %s)
                    """)
            mycursor.execute(query, (book_name, created_member_id,))
            book_id = mycursor.lastrowid
            query = ("""
                        INSERT INTO collaborator (collaborator_id, book_id)
                        VALUES (%s, %s)
                    """)
            mycursor.execute(query, (created_member_id, book_id))
            mycursor.execute("COMMIT")
            return "SUCCESS"
            
        except mysql.connector.Error as err:
            print("Something went wrong when creating book: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    def delete_book(created_member_id, book_id):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        DELETE FROM account_book 
                        WHERE created_member_id = %s AND id = %s
                    """)
            mycursor.execute(query, (created_member_id, book_id))
            rows_affected = mycursor.rowcount
            connection_object.commit() 
            if rows_affected:
                return "SUCCESS"
            else:
                return None
            
        except mysql.connector.Error as err:
            print("Something went wrong when deleting book: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

        
    def update_book(book_name, created_member_id, book_id):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        UPDATE account_book 
                        SET book_name = %s
                        WHERE created_member_id = %s AND id = %s
                    """)
            mycursor.execute(query, (book_name, created_member_id, book_id))
            rows_affected = mycursor.rowcount
            connection_object.commit() 
            if rows_affected:
                return "SUCCESS"
            else:
                return None
            
        except mysql.connector.Error as err:
            print("Something went wrong when updating book: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()
