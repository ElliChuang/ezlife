from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
import jwt
from config import TOKEN_PW


# 建立 Flask Blueprint
account_books = Blueprint("account_books", __name__)

@account_books.route("/api/account_books", methods=["GET", "POST", "DELETE", "PUT"])
def book():
    # 取得帳簿資訊
    if request.method == "GET":
        if "token" not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403
        try:
            token = session["token"]
            decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
            member_id = decode_data["id"]
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
            # 尚無預訂行程
            if not results: 
                return jsonify({"data" : None}),200
            # respose data
            datas = []
            for item in results:
                data = {
                        "account_book" : {
                            "id" : item["id"],
                            "book_name" : item["book_name"],
                            "created_member_id" : item["created_member_id"],
                        },
                }
                datas.append(data)
            
            return jsonify({
                        "data": datas
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when get account_book: {}".format(err))
            return jsonify({
                "error": True,
                "data" : "INTERNAL_SERVER_ERROR",             
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

    # 建立帳簿
    if request.method == "POST":
        data = request.get_json()
        book_name = data["bookName"]
        if book_name == "":
            return jsonify({
                        "error": True,
                        "data" : "請輸入帳簿名稱",             
                    }),400

        if "token" not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403
        try:
            token = session["token"]
            decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
            member_id = decode_data["id"]
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            
            # 確認帳簿名稱是否重複
            query = ("SELECT book_name FROM account_book WHERE book_name = %s AND created_member_id = %s")
            mycursor.execute(query, (book_name, member_id))
            result = mycursor.fetchone()
            if result:
                return jsonify({
                            "error": True,
                            "data" : "帳簿名稱已重複，請重新輸入",             
                        }),400

            else:
                mycursor.execute("START TRANSACTION")

                book_query = ("""
                    INSERT INTO account_book (book_name, created_member_id)
                    VALUES (%s, %s)
                """)
                book_value = (book_name, member_id)
                mycursor.execute(book_query, book_value)
                book_id = mycursor.lastrowid

                collaborator_query = ("""
                    INSERT INTO collaborator (collaborator_id, book_id)
                    VALUES (%s, %s)
                """)
                collaborator_value = (member_id, book_id)
                mycursor.execute(collaborator_query, collaborator_value)

                mycursor.execute("COMMIT")

                return jsonify({
                            "ok": True,          
                        }),200

        except mysql.connector.Error as err:
            print("Something went wrong when insert into account_book: {}".format(err))
            mycursor.execute("ROLLBACK")
            return jsonify({
                "error": True,
                "data" : "INTERNAL_SERVER_ERROR",             
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    # 刪除帳簿
    if request.method == "DELETE":
        if "token" not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        try:
            token = session["token"]
            data = request.get_json()
            book_id = data["bookId"]
            decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
            created_member_id = decode_data["id"]
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor()

            query = ("DELETE FROM account_book WHERE created_member_id = %s AND id = %s")
            mycursor.execute(query, (created_member_id, book_id))
            connection_object.commit() 
            rows_affected = mycursor.rowcount
            if rows_affected == 0:
                return jsonify({
                        "error": True,
                        "data": "無刪除權限，請洽帳簿管理員"    
                    }),400 
            
            return jsonify({
                        "ok": True    
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when delete account_book: {}".format(err))
            return jsonify({
                "error" : True,
                "data" : "INTERNAL_SERVER_ERROR"
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    # 修改帳簿名稱
    if request.method == "PUT":
        if "token" not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403
        
        data = request.get_json()
        book_name = data["bookName"]
        book_id = data["bookId"]
        if book_name == "":
            return jsonify({
                        "error": True,
                        "data" : "請輸入帳簿名稱",             
                    }),400

        try:
            token = session["token"]
            decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
            created_member_id = decode_data["id"]
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor()
            query = ("SELECT book_name FROM account_book WHERE book_name = %s AND created_member_id = %s")
            mycursor.execute(query, (book_name, created_member_id))
            result = mycursor.fetchone()
            if result:
                return jsonify({
                            "error": True,
                            "data" : "帳簿名稱已重複，請重新輸入",             
                        }),400
            
            query = ("""
                UPDATE account_book 
                SET book_name = %s
                WHERE created_member_id = %s AND id = %s""")
            mycursor.execute(query, (book_name, created_member_id, book_id))
            connection_object.commit()
            rows_affected = mycursor.rowcount
            if rows_affected == 0:
                return jsonify({
                            "error": True,
                            "data": "無編輯權限，請洽帳簿管理員"    
                        }),400 
            
            return jsonify({
                        "ok": True,
                        "data":{
                            "book_name" : book_name,
                            "book_id" : book_id
                        }
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when modify book name: {}".format(err))
            return jsonify({
                "error" : True,
                "data" : "INTERNAL_SERVER_ERROR"
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()