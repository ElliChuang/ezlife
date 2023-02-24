from flask import *
from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL 
import jwt
from config import TOKEN_PW
import json

# 建立 Flask Blueprint
record = Blueprint("record", __name__)


@record.route("/api/account_book/<int:bookId>/record", methods=["GET"])
def get_record(bookId):
    # 取得結算紀錄
    if request.method == "GET":
        if "token"  not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        
        try:
            account_dt = request.args.get("account_dt")
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query_start = ("""
                    SELECT 
                        m.name, 
                        sum(p.payable) as payable,
                        sum(p.prepaid) as prepaid,
                        s.account_dt,
                        m2.name as account_member
                    FROM journal_list_price as p
                    INNER JOIN journal_list as j on j.id = p.journal_list_id
                    INNER JOIN member as m on m.id = p.member_id
                    INNER JOIN status as s ON j.id = s.journal_list_id
                    INNER JOIN member as m2 ON m2.id = s.account_member_id
                    WHERE 	
                        j.book_id = %s 
                        AND s.status = %s  
                """)
            query_end = ("""
                    group by
                        s.account_dt,
                        s.account_member_id,
                        m.name
                    order by 
                        s.account_dt,
                        m.name;
                """)

            value = (bookId, '已結算')
            if account_dt:
                query_start += " AND s.account_dt = %s"
                value += (account_dt,)

            query = query_start + query_end
            mycursor.execute(query, value)
            results = mycursor.fetchall()
            if not results:
                    return jsonify({
                                "data" : "無結算紀錄"             
                            }),200

            dict = {}
            for i in results:
                key = i["account_dt"].strftime('%Y-%m-%d %H:%M:%S')
                if key not in dict:
                    dict[key] = {
                        "account_dt" : key,
                        "account_member" : i["account_member"],
                        "records" : []}
                record = {
                    "name": i["name"],
                    "payable" : i["payable"],
                    "prepaid": i["prepaid"]}

                dict[key]["records"].append(record)
            
            output = list(dict.values())
                
            return jsonify({
                            "ok" : True,
                            "data" : output             
                        }),200
            

        except mysql.connector.Error as err:
                print("Something went wrong when get record: {}".format(err))
                return jsonify({
                    "error": True,
                    "data" : "INTERNAL_SERVER_ERROR",             
                }),500
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()
