from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL


class UserModel():
    def get_user_by_email(email):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("SELECT * FROM member where email = %s")
            mycursor.execute(query, (email,))
            result = mycursor.fetchone()
            if result:
                user = {
                    "id" : result["id"],
					"name" : result["name"],
					"email" : result["email"],
                    "password" : result["password"],
					"profile" : result["profile"],
                }
                return user
            else:
                return None
            
        except mysql.connector.Error as err:
            print("Something went wrong when get user by email: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()
    

    def create_user(name, email, password, profile):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("INSERT INTO member (name, email, password, profile) VALUES (%s, %s, %s, %s)")
            value = (name, email, password, profile)
            mycursor.execute(query, value)
            connection_object.commit() 
            # 取得 user id
            user_id = mycursor.lastrowid
            return user_id

        except mysql.connector.Error as err:
            print("Something went wrong when updatingt user: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    def update_user_with_profile(name, email, profile, id):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        UPDATE member 
                        SET name = %s, email = %s, profile = %s 
                        WHERE id = %s
                    """)
            value = (name, email, profile, id)
            mycursor.execute(query, value)
            connection_object.commit() 
            return "SUCCESS"

        except mysql.connector.Error as err:
            print("Something went wrong when updatingt user with profile: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

    
    def update_user_without_profile(name, email, id):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        UPDATE member 
                        SET name = %s, email = %s
                        WHERE id = %s
                    """)
            value = (name, email, id)
            mycursor.execute(query, value)
            connection_object.commit() 
            return "SUCCESS"

        except mysql.connector.Error as err:
            print("Something went wrong when updateing user without profile: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()





