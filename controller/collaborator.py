from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
import jwt
from config import TOKEN_PW

# 建立 Flask Blueprint
collaborator = Blueprint("collaborator", __name__)

@collaborator.route("/api/collaborator", methods=["POST", "DELETE"])
def set_collaborator():
    # 新增共同編輯者
    if request.method == "POST":
        data = request.get_json()
        email = data["email"]
        book_id = data["bookId"]
        if email == "" or book_id == "":
            return jsonify({
                        "error": True,
                        "data" : "請輸入信箱及帳簿編號",             
                    }),400

        if "token"  not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403
        try:
            token = session["token"]
            decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
            created_member_id = decode_data["id"]
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("SELECT * FROM account_book WHERE created_member_id = %s AND id = %s")
            mycursor.execute(query, (created_member_id, book_id))
            result = mycursor.fetchone()
            if not result:
                    return jsonify({
                        "error": True,
                        "data" : "無新增權限，請洽帳簿管理員",             
                    }),403
           
            query = ("SELECT id, name FROM member WHERE email = %s")
            mycursor.execute(query, (email,))
            result = mycursor.fetchone()
            if not result:
                return jsonify({
                        "error": True,
                        "data" : "查無此會員",             
                    }),403
            
            collaborator_id = result["id"]
            query = ("INSERT INTO collaborator (collaborator_id, book_id) VALUE (%s, %s) ")
            value = (collaborator_id, book_id)
            mycursor.execute(query, value)
            connection_object.commit() 
            return jsonify({
                        "ok": True, 
                        "data": result["name"]         
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when insert into collaborator: {}".format(err))
            return jsonify({
                "error": True,
                "data" : "INTERNAL_SERVER_ERROR",             
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    # 刪除共同編輯者
    if request.method == "DELETE":
        if "token"  not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        data = request.get_json()
        collaborator_id = data["collaboratorId"]
        book_id = data["bookId"]

        try:
            token = session["token"]
            decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
            created_member_id = decode_data["id"]
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("SELECT * FROM account_book WHERE created_member_id = %s AND id = %s")
            mycursor.execute(query, (created_member_id, book_id))
            result = mycursor.fetchone()
            if not result:
                    return jsonify({
                        "error": True,
                        "data" : "無刪除權限，請洽帳簿管理員",             
                    }),403
            
            query = ("DELETE FROM collaborator WHERE collaborator_id = %s AND book_id = %s")
            mycursor.execute(query, (collaborator_id, book_id))
            connection_object.commit() 
            return jsonify({
                        "ok": True    
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when delete collaborator: {}".format(err))
            return jsonify({
                "error": True,
                "data" : "INTERNAL_SERVER_ERROR",             
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()