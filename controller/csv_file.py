from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
import pandas as pd

# 建立 Flask Blueprint
csv_file = Blueprint("csv_file", __name__)

@csv_file.route("/api/account_book/<int:bookId>/csv_file", methods=["GET"])
def download(bookId):
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
            journal_list = {"data": "查無帳目明細"}
            df = pd.DataFrame(journal_list, index = [0])
            df.to_csv(f'csv/data.csv', index = False)
            return send_from_directory('csv', 'data.csv', as_attachment=True)

        # respose data
        journal_list = []
        for item in results:
            date = item["date"].strftime('%Y-%m-%d')
            data = {
                    "日期" : date,
                    "生活機能" : item["category_main"],
                    "消費型態" : item["category_object"],
                    "支出對象" : item["category_character"],
                    "關鍵字" : item["keyword"],
                    "金額" : item["price"],
            }
            journal_list.append(data)
        

        # Generate a CSV file from the results
        df = pd.DataFrame(journal_list)
        df.to_csv(f'csv/data.csv', index = False)

        return send_from_directory('csv', 'data.csv', as_attachment=True)


    except mysql.connector.Error as err:
        print("Something went wrong when get csv_infor: {}".format(err))
        return jsonify({
            "error": True,
            "data" : "INTERNAL_SERVER_ERROR",             
        }),500

    finally:
        if connection_object.is_connected():
            mycursor.close()
            connection_object.close()


    