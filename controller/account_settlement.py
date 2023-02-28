from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
import jwt
import datetime
import pytz
from config import TOKEN_PW

# 建立 Flask Blueprint
account_settlement = Blueprint("account_settlement", __name__)


@account_settlement.route("/api/account_book/<int:bookId>/account_settlement", methods=["GET", "POST"])
def checkout(bookId):
    # 取得結帳明細
    if request.method == "GET":
        if "token"  not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        year = int(request.args.get("year"))
        month = int(request.args.get("month"))
        collaborator_id = request.args.get("collaborator_id")
        start_dt = ""
        end_dt = ""
        if month == 12:
            start_dt = f'{year}-{month}-01'
            end_dt = f'{year + 1}-01-01'
        else:
            start_dt = f'{year}-{month}-01'
            end_dt = f'{year}-{month + 1}-01'

        if not year or not month:
            return jsonify({
                        "error": True,
                        "data" : "請輸入欲查詢的年度及月份",             
                    }),403

        try:
            # 取得代墊及分攤金額
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                SELECT 
                    m.id, 
                    m.name, 
                    sum(p.payable) as payable,
                    sum(p.prepaid) as prepaid
                FROM journal_list_price as p
                INNER JOIN journal_list as j on j.id = p.journal_list_id
                INNER JOIN member as m on m.id = p.member_id
                INNER JOIN status as s ON j.id = s.journal_list_id
                WHERE 	
                    j.book_id = %s 
                    AND j.date >= %s 
                    AND j.date < %s
                    AND s.status = %s
                group by
                    m.id;
            """)
            mycursor.execute(query, (bookId, start_dt, end_dt, '未結算'))
            overview = mycursor.fetchall()
            if not overview:
                return jsonify({
                            "data" : "該月份無未結算項目"             
                        }),200
            else:
                # 取得結帳明細
                query_detail_basic = """
                    SELECT 
                        s.journal_list_id, 
                        m.id, 
                        m.name, 
                        p.payable, 
                        s.status, 
                        j.date, 
                        SUM(p.payable) OVER (PARTITION BY m.id) AS total_payable,
                        c1.name as category_main,
                        c2.name as category_object,
                        c3.name as category_character,
                        k.content as keyword
                    FROM journal_list_price as p
                    INNER JOIN journal_list as j on j.id = p.journal_list_id
                    INNER JOIN member as m on m.id = p.member_id
                    INNER JOIN journal_list_category jc1 ON j.id = jc1.journal_list_id
                    INNER JOIN categories c1 ON jc1.categories_id = c1.id AND c1.parent_category_id = 1
                    INNER JOIN journal_list_category jc2 ON j.id = jc2.journal_list_id
                    INNER JOIN categories c2 ON jc2.categories_id = c2.id AND c2.parent_category_id = 2
                    INNER JOIN journal_list_category jc3 ON j.id = jc3.journal_list_id
                    INNER JOIN categories c3 ON jc3.categories_id = c3.id AND c3.parent_category_id = 3
                    INNER JOIN journal_list_keyword jk ON j.id = jk.journal_list_id
                    LEFT JOIN keyword k ON jk.keyword_id = k.id 
                    INNER JOIN status as s ON j.id = s.journal_list_id
                    WHERE 
                        j.book_id = %s 
                        AND j.date >= %s 
                        AND j.date < %s
                        AND s.status = %s    
                """
                query_detail_end = "Order by j.date DESC, j.id DESC;"
                value_detail = (bookId, start_dt, end_dt, '未結算')

                condition = []
                if collaborator_id:
                    condition.append("m.id = %s")
                if condition:
                    query_detail_basic += " AND " + " AND ".join(condition)
                    value_detail = (bookId, start_dt, end_dt, '未結算', collaborator_id)
                
                query_detail = (query_detail_basic+ " " + query_detail_end)
                mycursor.execute(query_detail, value_detail)
                results = mycursor.fetchall()
                if not results:
                    return jsonify({
                                "data" : "該月份無未結算項目"        
                            }),200
                else:        
                     # respose data
                    journal_list = []
                    for item in results:
                        date = item["date"].strftime('%Y-%m-%d')
                        day = item["date"].strftime('%a')
                        if item["keyword"]:
                            data = {
                                    "id" : item["journal_list_id"],
                                    "date" : date,
                                    "day" : day,
                                    "category_main" : item["category_main"],
                                    "category_object" : item["category_object"],
                                    "category_character" : item["category_character"],
                                    "name" : item["name"],
                                    "keyword" : item["keyword"],
                                    "price" : item["payable"],
                            }
                        else:
                            data = {
                                    "id" : item["journal_list_id"],
                                    "date" : date,
                                    "day" : day,
                                    "category_main" : item["category_main"],
                                    "category_object" : item["category_object"],
                                    "category_character" : item["category_character"],
                                    "name" : item["name"],
                                    "keyword" : "",
                                    "price" : item["payable"],
                            }
                        journal_list.append(data)
 

                    return jsonify({
                                "data":{
                                        "overview" : overview,
                                        "status" : results[0]["status"],
                                        "period" : str(year) + "-" + str(month),
                                        "journal_list" : journal_list  
                                        }
                            }),200

        except mysql.connector.Error as err:
                print("Something went wrong when checkout: {}".format(err))
                return jsonify({
                    "error": True,
                    "data" : "INTERNAL_SERVER_ERROR",             
                }),500
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

    # 送出結算
    if request.method == "POST":
        data = request.get_json()
        year = int(data["year"])
        month = int(data["month"])
        start_dt = ""
        end_dt = ""
        if month == 12:
            start_dt = f'{year}-{month}-01'
            end_dt = f'{year + 1}-01-01'
        else:
            start_dt = f'{year}-{month}-01'
            end_dt = f'{year}-{month + 1}-01'

        if year == "" or month == "":
            return jsonify({
                        "error": True,
                        "data" : "請輸入欲結帳年度及月份",             
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
            member_name = decode_data["name"]
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                SELECT s.journal_list_id
                FROM status s
                INNER JOIN journal_list j ON j.id = s.journal_list_id
                WHERE 
                    j.book_id = %s 
                    AND j.date >= %s 
                    AND j.date < %s
                    AND s.status = %s    
            """)
            value = (bookId, start_dt, end_dt, "未結算")
            mycursor.execute(query, value)
            results = mycursor.fetchall()
            if not results:
                return jsonify({
                        "data": "無未結算項目"    
                    }),200

            value = []
            taiwan_tz = pytz.timezone('Asia/Taipei')
            now_taiwan = datetime.datetime.now(taiwan_tz)
            account_dt = now_taiwan.strftime('%Y%m%d%H%M%S')
            for item in results:
                value.append(("已結算", member_id, account_dt, item["journal_list_id"]))

            mycursor.executemany("""
                UPDATE status 
                SET status = %s, account_member_id = %s, account_dt = %s
                WHERE journal_list_id = %s
            """, value)
            connection_object.commit() 

            return jsonify({
                        "ok": True,
                        "data":{
                            "collaborator_id": member_id,
                            "collaborator_name" : member_name
                        }          
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when update status: {}".format(err))
            mycursor.execute("ROLLBACK")
            return jsonify({
                "error": True,
                "data" : "INTERNAL_SERVER_ERROR",             
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

     
            



   