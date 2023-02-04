from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
import jwt
import datetime
from config import TOKEN_PW

# 建立 Flask Blueprint
chart = Blueprint("chart", __name__)

@chart.route("/api/account_book/<int:bookId>/chart", methods=["GET"])
def chart_data(bookId):
    if "token" not in session:
        return jsonify({
                    "error": True,
                    "data" : "請先登入會員",             
                }),403
    year = request.args.get("year")
    month = request.args.get("month")
    if not year or not month:
        return jsonify({
            "error": True,
            "data" : "請輸入欲查詢的年度及月份",             
        }),403
    try:
        category_main = request.args.get("main")
        category_character = request.args.get("character")
        category_object = request.args.get("object")
        keyword = request.args.get("keyword")
        connection_object = MySQL.conn_obj()
        mycursor = connection_object.cursor(dictionary=True)
        
        # 圓餅圖
        query_chart = ('''
            SELECT SUM(price) AS total, category_main AS category 
            FROM journal_list 
            WHERE book_id = %s AND YEAR(date) = %s AND MONTH(date) = %s 
            GROUP BY category_main 
            UNION
            SELECT SUM(price) AS total, category_character AS category 
            FROM journal_list 
            WHERE book_id = %s AND YEAR(date) = %s AND MONTH(date) = %s 
            GROUP BY category_character;
        ''')
        value_chart = (bookId, year, month, bookId, year, month)
        mycursor.execute(query_chart, value_chart)
        results_chart = mycursor.fetchall()

        chart_main = {"食":0, "衣":0, "住":0, "行":0, "育":0, "樂":0}
        chart_character = {"個人":0, "家庭":0, "育兒":0, "寵物":0,"宿舍":0, "旅行":0}
        for item in results_chart:
            if item["category"] in chart_main:
                chart_main[item["category"]] = int(item["total"])
            if item["category"] in chart_character:   
                chart_character[item["category"]] = int(item["total"])
        
        # 明細賬
        query_basic = """
            SELECT 
                j.id,
                j.date, 
                j.category_object,  
                j.category_character,  
                j.keyword, 
                j.price,
                subq.category_main, 
                subq.category_main_sum
            FROM 
        """
        subquery_basic = """
            (SELECT 
                category_main, 
                SUM(price) AS category_main_sum
            FROM 
                journal_list
            WHERE 
                book_id = %s 
                AND YEAR(date) = %s
                AND MONTH(date) = %s 
        """

        subquery_end = """
            GROUP BY 
                category_main 
            ) AS subq
        """

        query_middle = """
            LEFT JOIN 
                journal_list AS j
            ON 
                subq.category_main = j.category_main
            WHERE 
                book_id = %s AND YEAR(date) = %s AND MONTH(date) = %s 
        """

        query_end = "Order by date DESC;"

        conditions = []
        sub_conditions = []
        basic_value = (bookId, year, month)
        if category_main:
            conditions.append("subq.category_main= %s")
            sub_conditions.append("category_main= %s")
            basic_value += (category_main,)

        if category_character:
            conditions.append("category_character= %s")
            sub_conditions.append("category_character= %s")
            basic_value += (category_character,)

        if category_object:
            conditions.append("category_object= %s")
            sub_conditions.append("category_object= %s")
            basic_value += (category_object,)
        
        if keyword:
            conditions.append("keyword like %s")
            sub_conditions.append("keyword like %s")
            basic_value += ("%" + keyword + "%",)

        if conditions and sub_conditions:
            query_middle += " AND " + " AND ".join(conditions)
            subquery_basic += " AND " + " AND ".join(sub_conditions)
        
        query = (query_basic+ " " + subquery_basic + " " + subquery_end + " " + query_middle + " " + query_end)
        value = basic_value + basic_value
        mycursor.execute(query, value)
        results = mycursor.fetchall()

        if not results:
            return jsonify({
                    "query_year" : year,
                    "query_month" : month,
                    "chart_main" : chart_main,
                    "chart_character" : chart_character,
                    "journal_list": "查無帳目明細"          
                    }),200

        # respose data
        journal_list = []
        journal_list_main={"食":0, "衣":0, "住":0, "行":0, "育":0, "樂":0}
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
            journal_list.append(data)
            journal_list_main[item["category_main"]] = int(item["category_main_sum"])
        
        amount = sum(journal_list_main.values())


        return jsonify({
                    "query_year" : year,
                    "query_month" : month,
                    "chart_main" : chart_main,
                    "chart_character" : chart_character,
                    "journal_list":{
                        "amount" : amount,
                        "category_main" : journal_list_main, 
                        "data":journal_list
                        } 
                }),200

    except mysql.connector.Error as err:
        print("Something went wrong when get chart_infor: {}".format(err))
        return jsonify({
            "error": True,
            "data" : "INTERNAL_SERVER_ERROR",             
        }),500

    finally:
        if connection_object.is_connected():
            mycursor.close()
            connection_object.close()


    