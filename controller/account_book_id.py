from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
import jwt
import datetime
import random
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
            year = request.args.get("year")
            month = request.args.get("month")
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                SELECT 
                    id,
                    date, 
                    category_main, 
                    category_object,  
                    category_character,  
                    keyword, 
                    price,
                    status
                FROM journal_list AS j 
                WHERE book_id = %s AND YEAR(date) = %s AND MONTH(date) = %s 
                Order by date DESC, id DESC;
            """)
            mycursor.execute(query, (bookId, year, month))
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
                                "status" : item["status"]
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
        payable = data["payable"]
        prepaid = data["prepaid"]
        status = "未結算"
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
        
        # insert into journal list table
        try:
            create_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            create_num = random.randrange(100,999)
            journal_list_id = create_time + str(create_num)
            token = session["token"]
            decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
            member_id = decode_data["id"]
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor()
            query = ("""
                INSERT INTO journal_list (
                    id,
                    date, 
                    category_main, 
                    category_object, 
                    category_character, 
                    keyword, 
                    price, 
                    book_id,
                    created_member_id,
                    status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """)
            value = (journal_list_id, date, category_main, category_object, category_character, keyword, price, bookId, member_id, status)
            mycursor.execute(query, value)
            connection_object.commit() 

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

        # insert into account_settlement table
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor()
            prepaid_dict = {item['collaborator_id']: item['price'] for item in prepaid}
            payable_dict = {item['collaborator_id']: item['price'] for item in payable}
            ids = set(prepaid_dict) | set(payable_dict)
            result = [{'collaborator_id': id, 'prepaid_price': prepaid_dict.get(id, 0), 'payable_price': payable_dict.get(id, 0)} for id in ids]
            for i in result:
                collaborator_id = i["collaborator_id"]
                payable = i["payable_price"]
                prepaid = i["prepaid_price"]
                query = ("""
                    INSERT INTO account_settlement (
                        journal_list_id,
                        date, 
                        collaborator_id,
                        payable, 
                        prepaid , 
                        status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """)
                value = (journal_list_id, date, collaborator_id, payable, prepaid , status)
                mycursor.execute(query, value)
                connection_object.commit() 
            return jsonify({
                        "ok": True,          
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when insert into account_settlement: {}".format(err))
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
            query = ("DELETE FROM journal_list WHERE id = %s AND status = %s")
            mycursor.execute(query, (id, '未結算'))
            rows_affected = mycursor.rowcount
            connection_object.commit() 
            if rows_affected == 0:
                return jsonify({
                        "data": "支出已結算，無法刪除。"    
                    }),200
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