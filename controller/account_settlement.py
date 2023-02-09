from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
import jwt
import datetime
import random
from config import TOKEN_PW

# 建立 Flask Blueprint
account_settlement = Blueprint("account_settlement", __name__)


@account_settlement.route("/api/account_book/<int:bookId>/account_settlement", methods=["GET", "POST", "DELETE"])
def checkout(bookId):
    # 取得結帳明細
    if request.method == "GET":
        if "token"  not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        year = request.args.get("year")
        month = request.args.get("month")
        collaborator_id = request.args.get("collaborator_id")
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
                    sum(s.payable) as payable,
                    sum(s.prepaid) as prepaid
                FROM account_settlement as s
                INNER JOIN member as m on m.id = s.collaborator_id
                INNER JOIN journal_list as j on j.id = s.journal_list_id
                WHERE j.book_id = %s AND year(s.date) = %s AND month(s.date) = %s AND s.status = %s
                GROUP By s.collaborator_id;
            """)
            mycursor.execute(query, (bookId, year, month, '未結算'))
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
                        s.collaborator_id, 
                        m.name, 
                        s.payable, 
                        s.status, 
                        s.date, 
                        s.modified_dt as account_dt,
                        SUM(s.payable) OVER (PARTITION BY s.collaborator_id) AS total_payable,
                        j.category_main,
                        j.category_object,
                        j.category_character,
                        j.keyword
                    FROM account_settlement as s
                    INNER JOIN member as m on m.id = s.collaborator_id
                    INNER JOIN journal_list as j on j.id = s.journal_list_id
                    WHERE j.book_id = %s AND year(s.date) = %s AND month(s.date) = %s AND s.status = %s
                    
                """
                query_detail_end = "Order by s.date DESC;"
                value_detail = (bookId, year, month, '未結算')

                condition = []
                if collaborator_id:
                    condition.append("s.collaborator_id = %s")
                if condition:
                    query_detail_basic += " AND " + " AND ".join(condition)
                    value_detail = (bookId, year, month, '未結算', collaborator_id)
                
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
                        journal_list.append(data)

                    account_day = results[0]["account_dt"]
                    if account_day:
                        account_day = account_day.strftime('%Y-%m-%d') 

                    return jsonify({
                                "data":{
                                        "overview" : overview,
                                        "status" : results[0]["status"],
                                        "account_day" : account_day,
                                        "period" : year + "-" + month,
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
        year = data["year"]
        month = data["month"]

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
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor()
            status = "已結算"

            # 更新 account_settlement table
            query_account_settlement = ("""
                UPDATE account_settlement as s
                INNER JOIN journal_list as j on j.id =  s.journal_list_id
                SET s.status = %s
                WHERE year(s.date) = %s AND month(s.date) = %s AND j.book_id = %s AND s.status = %s 
                AND j.id IN (SELECT id FROM journal_list WHERE book_id = %s AND status = %s);
            """)
            value_account_settlement = (status, year, month, bookId, "未結算",bookId, "未結算")
            mycursor.execute(query_account_settlement, value_account_settlement)
            connection_object.commit() 

            # 更新 journal_list table
            query_journal_list = ("""
                UPDATE journal_list as j
                INNER JOIN account_settlement as s on s.journal_list_id = j.id 
                SET j.status = %s
                WHERE year(j.date) = %s AND month(j.date) = %s AND j.book_id = %s AND j.status = %s
                AND j.id IN (SELECT journal_list_id FROM account_settlement WHERE status = %s);
            """)
            value_journal_list = (status, year, month, bookId, '未結算', '未結算')
            mycursor.execute(query_journal_list, value_journal_list)
            connection_object.commit() 

            return jsonify({
                        "ok": True,          
                    }),200

        except mysql.connector.Error as err:
            print("Something went wrong when update status: {}".format(err))
            return jsonify({
                "error": True,
                "data" : "INTERNAL_SERVER_ERROR",             
            }),500

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

     
            



   