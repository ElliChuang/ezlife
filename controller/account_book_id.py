from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
import jwt
import datetime
from config import TOKEN_PW

# 建立 Flask Blueprint
account_book_id = Blueprint("account_book_id", __name__)


@account_book_id.route("/api/account_book/<int:bookId>", methods=["GET", "POST", "DELETE"])
def journal_list(bookId):
    # 取得日記帳明細
    if request.method == "GET":
        if "token"  not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            # current_year = datetime.now().year
            # current_month = datetime.now().month
            query = ("""
                SELECT 
                    id,
                    date, 
                    category_main, 
                    category_object,  
                    category_character,  
                    keyword, 
                    price
                FROM journal_list AS j 
                WHERE book_id = %s 
                Order by date DESC;
            """)
            mycursor.execute(query, (bookId,))
            results = mycursor.fetchall()
            if not results:
                return jsonify({
                            "data" : {"message" : "尚無新增項目"}             
                        }),200
            else:
                # respose data
                datas = []
                for item in results:
                    date = item["date"].strftime('%Y-%m-%d')
                    day = item["date"].strftime('%a')

                    data = {
                            "journal_list" : {
                                "id" : item["id"],
                                "date" : date,
                                "day" : day,
                                "category_main" : item["category_main"],
                                "category_object" : item["category_object"],
                                "category_character" : item["category_character"],
                                "keyword" : item["keyword"],
                                "price" : item["price"],
                            },
                    }
                    datas.append(data)
                
                return jsonify({
                            "data": datas
                        }),200
        except mysql.connector.Error as err:
                print("Something went wrong when get journal_list: {}".format(err))
                return jsonify({
                    "error": True,
                    "data" : "INTERNAL_SERVER_ERROR",             
                }),500
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

    # 建立日記帳
    if request.method == "POST":
        data = request.get_json()
        date = data["date"]
        category_main = data["category_main"]
        category_object = data["category_object"]
        category_character = data["category_character"]
        keyword = data["keyword"]
        price = data["price"]
        if date == "" or category_main == "" or category_object == "" or category_character == "" or keyword == "" or price == "":
            return jsonify({
                        "error": True,
                        "data" : "欄位填寫不完整",             
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
            mycursor = connection_object.cursor()
            query = ("""
                INSERT INTO journal_list (
                    date, 
                    category_main, 
                    category_object, 
                    category_character, 
                    keyword, 
                    price, 
                    book_id,
                    created_member_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """)
            value = (date, category_main, category_object, category_character, keyword, price, bookId, member_id)
            mycursor.execute(query, value)
            connection_object.commit() 
            return jsonify({
                        "ok": True,          
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when create journal list: {}".format(err))
            return jsonify({
                "error": True,
                "data" : "INTERNAL_SERVER_ERROR",             
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    # 刪除日記帳
    if request.method == "DELETE":
        if "token" not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        try:
            data = request.get_json()
            id = data["id"]
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor()
            query = ("DELETE FROM journal_list WHERE id = %s")
            mycursor.execute(query, (id,))
            connection_object.commit() 
            return jsonify({
                        "ok": True    
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when delete journal list: {}".format(err))
            return jsonify({
                "error": True,
                "data" : "INTERNAL_SERVER_ERROR",             
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()