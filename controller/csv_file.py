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

    year = int(request.args.get("year"))
    month = int(request.args.get("month"))
    if not year or not month:
        return jsonify({
            "error": True,
            "data" : "請輸入欲查詢的年度及月份",             
        }),403

    try:
        category_main = request.args.get("main").lower()
        category_character = request.args.get("character").lower()
        category_object = request.args.get("object").lower()
        keyword = request.args.get("keyword").lower()
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
        
        # 明細賬
        query_basic = """
            SELECT 
                j.id,
                j.date, 
                j.amount,
                c1.name as category_main,
                c2.name as category_object,
                c3.name as category_character,
                k.content as keyword,
        
        """
        subquery_basic = """
            (SELECT sum(j.amount) 
            FROM journal_list j
            INNER JOIN journal_list_category jc 
                ON j.id = jc.journal_list_id
            INNER JOIN categories c 
                ON jc.categories_id = c.id AND c.parent_category_id = 1
        """

        subquery_end = """
            WHERE 
                j.book_id = %s 
                AND j.date >= %s 
                AND j.date < %s 
                AND c.name = C1.name 
            GROUP BY 
                c.name
            ) AS category_main_sum
        """

        query_middle = """
            FROM journal_list AS j
            INNER JOIN journal_list_category jc1 
                ON j.id = jc1.journal_list_id
            INNER JOIN categories C1 
                ON jc1.categories_id = C1.id AND C1.parent_category_id = 1
            INNER JOIN journal_list_category jc2 
                ON j.id = jc2.journal_list_id
            INNER JOIN categories c2 
                ON jc2.categories_id = c2.id AND c2.parent_category_id = 2
            INNER JOIN journal_list_category jc3 
                ON j.id = jc3.journal_list_id
            INNER JOIN categories c3 
                ON jc3.categories_id = c3.id AND c3.parent_category_id = 3
            INNER JOIN journal_list_keyword jk 
                ON j.id = jk.journal_list_id
            INNER JOIN keyword k 
                ON jk.keyword_id = k.id
            WHERE 
                j.book_id = %s 
                AND j.date >= %s 
                AND j.date < %s  
        """

        query_end = """
            Order by 
                j.date DESC,
                j.id DESC;
        """

        conditions = []
        sub_conditions = []
        basic_value = (bookId, start_dt, end_dt)
        append_value = ()
        if category_main:
            conditions.append("c1.name = %s")
            sub_conditions.append("""
                INNER JOIN journal_list_category jc1 
                ON j.id = jc1.journal_list_id
                INNER JOIN categories c1 
                ON jc1.categories_id = c1.id AND c1.name = %s""")
            append_value += (category_main,)

        if category_character:
            conditions.append("c3.name = %s")
            sub_conditions.append("""
                INNER JOIN journal_list_category jc3
                ON j.id = jc3.journal_list_id
                INNER JOIN categories c3 
                ON jc3.categories_id = c3.id AND c3.name = %s""")
            append_value += (category_character,) 

        if category_object:
            conditions.append("c2.name = %s")
            sub_conditions.append("""
                INNER JOIN journal_list_category jc2 
                ON j.id = jc2.journal_list_id
                INNER JOIN categories c2 
                ON jc2.categories_id = c2.id AND c2.name = %s""")
            append_value += (category_object,) 
        
        if keyword:
            conditions.append("k.content like %s")
            sub_conditions.append("""
                INNER JOIN journal_list_keyword jk ON j.id = jk.journal_list_id
                INNER JOIN keyword k ON jk.keyword_id = k.id 
                AND keyword like %s""")
            append_value += ("%" + keyword + "%",)

        if conditions and sub_conditions:
            query_middle += " AND " + " AND ".join(conditions)
            subquery_basic += " ".join(sub_conditions)
        
        query = (query_basic+ " " + subquery_basic + " " + subquery_end + " " + query_middle + " " + query_end)
        value = append_value + basic_value + basic_value + append_value
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
                    "金額" : item["amount"],
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


    