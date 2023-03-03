from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
import jwt
from config import TOKEN_PW

# 建立 Flask Blueprint
account_book_auth = Blueprint("account_book_auth", __name__)

@account_book_auth.route("/api/account_book_auth/<int:bookId>", methods=["GET"])
def book_auth(bookId):
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
            SELECT m.id, m.name, b.book_name, m2.name as host_member FROM collaborator AS c
            INNER JOIN member AS m ON m.id = c.collaborator_id
            INNER JOIN account_book AS b ON c.book_id = b.id
            INNER JOIN member AS m2 ON b.created_member_id = m2.id
            WHERE c.book_id = %s 
            ORDER BY m.name
        """)
        mycursor.execute(query, (bookId,))
        result = mycursor.fetchall()
        for item in result:
            if item['id'] == int(member_id):
                return jsonify({
                        "ok": True,
                        "data" : result          
                    }),200
            else:
                continue
        return jsonify({
                    "error": True,
                    "data" : "無帳簿權限",             
                }),403

    except mysql.connector.Error as err:
        print("Something went wrong when get book_auth: {}".format(err))
        return jsonify({
            "error": True,
            "data" : "INTERNAL_SERVER_ERROR",             
        }),500

    finally:
        if connection_object.is_connected():
            mycursor.close()
            connection_object.close()


    