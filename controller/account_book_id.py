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
                    j.id,
                    j.date, 
                    j.category1, 
                    j.category2,  
                    j.category3,  
                    j.remark, 
                    j.price, 
                    b.book_name,
                    (SELECT m.name FROM member AS m INNER JOIN account_book AS b on b.host_id = m.id WHERE b.id = %s) AS host_name,
                    group_concat(concat("id",":",m.id,"name",":",m.name))AS collaborator 
                FROM journal_list AS j 
                LEFT JOIN account_book AS b on b.id = j.book_id
                LEFT JOIN collaborator AS c on b.id = c.book_id 
                LEFT JOIN member AS m on m.id = c.collaborator_id  
                WHERE b.id = %s
                GROUP BY host_name,j.id,j.date,j.category1,j.category2,j.category3,j.remark,j.price,b.id 
                Order by j.date DESC;
            """)
            value = (bookId,bookId)
            mycursor.execute(query, value)
            results = mycursor.fetchall()
            if not results:
                query = ('SELECT book_name FROM account_book WHERE id = %s')
                mycursor.execute(query, (bookId,))
                result = mycursor.fetchone()
                return jsonify({
                            "data" : {
                                "message" : "尚無新增項目",
                                "book_name" : result['book_name']
                                }             
                        }),200
            else:
                collaborator = results[0]["collaborator"]
                editors = []
                if collaborator:
                    data = collaborator.split(',')
                    for item in data:
                        id = int(item.split(':')[1].split('name')[0])
                        name = item.split(':')[2]
                        editors.append({'id': id, 'name': name})
                # respose data
                datas = []
                for item in results:
                    date = item["date"].strftime('%Y-%m-%d')
                    day = item["date"].strftime('%a')

                    data = {
                            "journal_list" : {
                                "id" : item["id"],
                                "book_name" : item["book_name"],
                                "collaborator" : editors,
                                "host_name" : item["host_name"],
                                "date" : date,
                                "day" : day,
                                "category1" : item["category1"],
                                "category2" : item["category2"],
                                "category3" : item["category3"],
                                "remark" : item["remark"],
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
        category1 = data["category1"]
        category2 = data["category2"]
        category3 = data["category3"]
        remark = data["remark"]
        price = data["price"]
        if date == "" or category1 == "" or category2 == "" or category3 == "" or remark == "" or price == "":
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
                    category1, 
                    category2, 
                    category3, 
                    remark, 
                    price, 
                    book_id,
                    created_member_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """)
            value = (date, category1, category2, category3, remark, price, bookId, member_id)
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