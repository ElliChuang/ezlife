from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
from model.db import Redis
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
            year = int(request.args.get("year"))
            month = int(request.args.get("month"))
            start_dt = ""
            end_dt = ""
            if month == 12:
                start_dt = f'{year}-{month}-01'
                end_dt = f'{year + 1}-01-01'
            else:
                start_dt = f'{year}-{month}-01'
                end_dt = f'{year}-{month + 1}-01'

            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)

            query = ("""
                SELECT 
                    j.id,
                    j.date,
                    j.amount,
                    c1.name as category_main,
                    c2.name as category_object,
                    c3.name as category_character,
                    k.content,
                    s.status
                FROM 
                    journal_list j 
                    INNER JOIN journal_list_category jc1 ON j.id = jc1.journal_list_id
                    INNER JOIN categories c1 ON jc1.categories_id = c1.id AND c1.parent_category_id = 1
                    INNER JOIN journal_list_category jc2 ON j.id = jc2.journal_list_id
                    INNER JOIN categories c2 ON jc2.categories_id = c2.id AND c2.parent_category_id = 2
                    INNER JOIN journal_list_category jc3 ON j.id = jc3.journal_list_id
                    INNER JOIN categories c3 ON jc3.categories_id = c3.id AND c3.parent_category_id = 3
                    INNER JOIN journal_list_keyword jk ON j.id = jk.journal_list_id
                    INNER JOIN keyword k ON jk.keyword_id = k.id 
                    INNER JOIN (
                        SELECT journal_list_id, status
                        FROM status
                        WHERE (journal_list_id, created_dt) IN (
                            SELECT journal_list_id, MAX(created_dt)
                            FROM status
                            GROUP BY journal_list_id
                            )
                    ) s ON j.id = s.journal_list_id
                WHERE 
                    j.book_id = %s 
                    AND j.date >= %s 
                    AND j.date < %s 
                ORDER BY 
                    j.date DESC, 
                    j.id DESC;
            """)
            mycursor.execute(query, (bookId, start_dt, end_dt))
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
                                "keyword" : item["content"],
                                "amount" : item["amount"],
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
        category_main = data["category_main"].lower()
        category_object = data["category_object"].lower()
        category_character = data["category_character"].lower()
        keyword = data["keyword"].lower()
        amount = data["amount"]
        payable = data["payable"]
        prepaid = data["prepaid"]
        if date == "" or category_main == "" or category_object == "" or category_character == "" or keyword == "" or amount == "":
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
            create_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            create_num = random.randrange(100,999)
            journal_list_id = create_time + str(create_num)

            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor()

            mycursor.execute("START TRANSACTION")

            journal_list_value = (journal_list_id, date, amount, bookId)
            mycursor.execute("""
                INSERT INTO journal_list (id, date, amount, book_id) 
                VALUES (%s, %s, %s, %s)""", journal_list_value)

            prepaid_dict = {item['collaborator_id']: item['price'] for item in prepaid}
            payable_dict = {item['collaborator_id']: item['price'] for item in payable}
            ids = set(prepaid_dict) | set(payable_dict)
            journal_list_price_value = [(journal_list_id, id, prepaid_dict.get(id, 0), payable_dict.get(id, 0)) for id in ids]
            mycursor.executemany("INSERT INTO journal_list_price (journal_list_id, member_id, prepaid, payable) VALUES (%s, %s, %s, %s)", journal_list_price_value)

            journal_list_category_value = (journal_list_id, category_main, category_object, category_character)
            mycursor.execute("""
                INSERT INTO journal_list_category (journal_list_id, categories_id) 
                SELECT %s, id FROM categories WHERE name IN (%s, %s, %s)""", journal_list_category_value)

            token = session["token"]
            decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
            member_id = decode_data["id"]
            status = "未結算"
            status_value = (journal_list_id, status, member_id)
            mycursor.execute("""
                INSERT INTO status (journal_list_id, status, member_id) 
                VALUES (%s, %s, %s)""", status_value)  

            keyword_id_in_redis = Redis.connect_to_redis().get(keyword)
            print(keyword_id_in_redis)
            if keyword_id_in_redis:
                print('I am in redis')
                journal_list_keyword_value = (journal_list_id, keyword_id_in_redis)
                mycursor.execute("""
                INSERT INTO journal_list_keyword (journal_list_id, keyword_id) 
                VALUES (%s, %s)""", journal_list_keyword_value)
            else:
                mycursor.execute("INSERT INTO keyword (content) VALUES (%s)", (keyword,))
                keyword_id = mycursor.lastrowid
                journal_list_keyword_value = (journal_list_id, keyword_id)
                mycursor.execute("""
                    INSERT INTO journal_list_keyword (journal_list_id, keyword_id) 
                    VALUES (%s, %s)""", journal_list_keyword_value)
                Redis.connect_to_redis().set(keyword, keyword_id)

            mycursor.execute("COMMIT")
            print("Transaction committed successfully!")

            return jsonify({
                        "ok": True,          
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when add journal_list: {}".format(err))
            mycursor.execute("ROLLBACK")
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
            query = ("""
                DELETE j FROM journal_list j
                INNER JOIN (
                        SELECT journal_list_id, status
                        FROM status
                        WHERE (journal_list_id, created_dt) IN (
                            SELECT journal_list_id, MAX(created_dt)
                            FROM status
                            GROUP BY journal_list_id
                            )
                    ) s ON j.id = s.journal_list_id
                WHERE j.id = %s AND s.status = %s
            """)
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