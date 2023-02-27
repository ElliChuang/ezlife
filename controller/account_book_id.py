from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
from model.db import Redis
import datetime
import random
import json
import pytz
from config import TOKEN_PW

# 建立 Flask Blueprint
account_book_id = Blueprint("account_book_id", __name__)


@account_book_id.route("/api/account_book/<int:bookId>", methods=["GET", "POST", "DELETE", "PATCH"])
def journal_list(bookId):
    # 取得日記帳明細
    if request.method == "GET":
        if "token"  not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403
        try:
            print("sever")
            year = int(request.args.get("year"))
            month = int(request.args.get("month"))
            print(year, month)
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
                    s.status,
                    group_concat(
                        CONCAT('{"member_name":"', p.name, '",'),
                        CONCAT('"member_id":"', p.member_id, '",'),
                        CONCAT('"payable":"',  p.payable, '",'),
                        CONCAT('"prepaid":"',  p.prepaid, '",'),
                    '"}') as situation
                FROM 
                    journal_list j 
                    INNER JOIN journal_list_category jc1 ON j.id = jc1.journal_list_id
                    INNER JOIN categories c1 ON jc1.categories_id = c1.id AND c1.parent_category_id = 1
                    INNER JOIN journal_list_category jc2 ON j.id = jc2.journal_list_id
                    INNER JOIN categories c2 ON jc2.categories_id = c2.id AND c2.parent_category_id = 2
                    INNER JOIN journal_list_category jc3 ON j.id = jc3.journal_list_id
                    INNER JOIN categories c3 ON jc3.categories_id = c3.id AND c3.parent_category_id = 3
                    INNER JOIN journal_list_keyword jk ON j.id = jk.journal_list_id
                    LEFT JOIN keyword k ON jk.keyword_id = k.id 
                    INNER JOIN status s ON j.id = s.journal_list_id
                    INNER JOIN (
                        SELECT p.journal_list_id, p.member_id, m.name as name, p.payable, p.prepaid
                        FROM journal_list_price p
                        INNER JOIN member m on m.id = p.member_id
                    ) p ON j.id = p.journal_list_id
                WHERE 
                    j.book_id = %s 
                    AND j.date >= %s 
                    AND j.date < %s 
                GROUP BY
                    j.id,
                    c1.name ,
                    c2.name ,
                    c3.name ,
                    k.content,
                    s.status
                ORDER BY 
                    j.date DESC, 
                    j.id DESC;
            """)
            mycursor.execute(query, (bookId, start_dt, end_dt))
            results = mycursor.fetchall()
            if not results:
                print("here")
                return jsonify({
                            "data" : "尚無新增項目"            
                        }),200
            else:
                # respose data
                datas = []
                for item in results:
                    date = item["date"].strftime('%Y-%m-%d')
                    day = item["date"].strftime('%a')
                    situation = item["situation"]
                    situation = situation.replace(',"}', "}")
                    if not item["content"]:
                        data = {
                                "journal_list" : {
                                    "id" : item["id"],
                                    "date" : date,
                                    "day" : day,
                                    "category_main" : item["category_main"],
                                    "category_object" : item["category_object"],
                                    "category_character" : item["category_character"],
                                    "keyword" : "",
                                    "amount" : item["amount"],
                                    "status" : item["status"],
                                    "situation" : json.loads("[" + situation + "]")
                                },
                        }
                    else:
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
                                    "status" : item["status"],
                                    "situation" : json.loads("[" + situation + "]")
                                },
                        }
                    datas.append(data)
                
                return jsonify({
                            "ok" : True,
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
        if date == "" or category_main == "" or category_object == "" or category_character == "" or amount == "":
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
            taiwan_tz = pytz.timezone('Asia/Taipei')
            now_taiwan = datetime.datetime.now(taiwan_tz)
            created_time = now_taiwan.strftime('%Y%m%d%H%M%S')
            create_num = random.randrange(100,999)
            journal_list_id = created_time + str(create_num)

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

            status = "未結算"
            status_value = (journal_list_id, status, created_time)
            mycursor.execute("""
                INSERT INTO status (journal_list_id, status, created_dt) 
                VALUES (%s, %s, %s)""", status_value)  

            if keyword:
                keyword_id_in_redis = Redis.connect_to_redis().get(keyword)
                if keyword_id_in_redis:
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
            else:
                mycursor.execute("""
                        INSERT INTO journal_list_keyword (journal_list_id) 
                        VALUES (%s)""", (journal_list_id,))

            mycursor.execute("COMMIT")

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
                INNER JOIN status s ON j.id = s.journal_list_id
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

    
    # 修改日記帳
    if request.method == "PATCH":
        data = request.get_json()
        date = data["date"]
        category_main = data["category_main"].lower()
        category_object = data["category_object"].lower()
        category_character = data["category_character"].lower()
        keyword = data["keyword"].lower()
        amount = data["amount"]
        payable = data["payable"]
        prepaid = data["prepaid"]
        journal_list_id = data["journal_list_id"]
        if date == "" or category_main == "" or category_object == "" or category_character == "" or amount == "":
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
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor()
            status_value = (journal_list_id, "已結算")
            mycursor.execute("""
                SELECT journal_list_id
                FROM status
                WHERE journal_list_id = %s AND status = %s
            """, status_value)
            result = mycursor.fetchone()
            if result:
                return jsonify({
                        "data": "支出已結算，無法編輯。"    
                    }),200
 
            mycursor.execute("START TRANSACTION")

            taiwan_tz = pytz.timezone('Asia/Taipei')
            now_taiwan = datetime.datetime.now(taiwan_tz)
            modified_time = now_taiwan.strftime('%Y%m%d%H%M%S')

            journal_list_value = ( date, amount, modified_time ,bookId, journal_list_id)
            mycursor.execute("""
                UPDATE journal_list 
                SET date = %s, amount = %s, modified_dt = %s
                WHERE book_id = %s AND id = %s
            """, journal_list_value)

            prepaid_dict = {item['collaborator_id']: item['price'] for item in prepaid}
            payable_dict = {item['collaborator_id']: item['price'] for item in payable}
            ids = set(prepaid_dict) | set(payable_dict)
            journal_list_price_value = [( prepaid_dict.get(id, 0), payable_dict.get(id, 0), modified_time ,journal_list_id, id ) for id in ids]
            mycursor.executemany("""
                UPDATE journal_list_price 
                SET prepaid = %s, payable = %s, modified_dt = %s
                WHERE journal_list_id = %s AND member_id = %s
            """, journal_list_price_value)

            journal_list_category_value = [
                    (category_main, journal_list_id, 1),
                    (category_object, journal_list_id, 2),
                    (category_character, journal_list_id, 3)]
            mycursor.executemany("""
                UPDATE journal_list_category jc
                INNER JOIN categories c ON c.id = jc.categories_id
                SET 
                    jc.categories_id = (SELECT id FROM categories WHERE name = %s)
                WHERE 
                    journal_list_id = %s
                    AND c.parent_category_id = %s
            """, journal_list_category_value)

            if keyword:
                keyword_id_in_redis = Redis.connect_to_redis().get(keyword)
                if keyword_id_in_redis:
                    journal_list_keyword_value = (keyword_id_in_redis, journal_list_id)
                    mycursor.execute("""
                        UPDATE journal_list_keyword 
                        SET keyword_id = %s
                        WHERE journal_list_id = %s
                    """, journal_list_keyword_value)
                else:
                    mycursor.execute("INSERT INTO keyword (content) VALUES (%s)", (keyword,))
                    keyword_id = mycursor.lastrowid
                    journal_list_keyword_value = (keyword_id, journal_list_id)
                    mycursor.execute("""
                        UPDATE journal_list_keyword 
                        SET keyword_id = %s
                        WHERE journal_list_id = %s""", journal_list_keyword_value)
                    Redis.connect_to_redis().set(keyword, keyword_id)
            else:
                 journal_list_keyword_value = (None, journal_list_id)
                 mycursor.execute("""
                        UPDATE journal_list_keyword 
                        SET keyword_id = %s
                        WHERE journal_list_id = %s""", journal_list_keyword_value)


            mycursor.execute("COMMIT")

            return jsonify({
                        "ok": True,          
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when edit journal_list: {}".format(err))
            mycursor.execute("ROLLBACK")
            return jsonify({
                "error": True,
                "data" : "INTERNAL_SERVER_ERROR",             
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()