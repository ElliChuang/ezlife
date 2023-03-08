from flask import *
from model.journal_list_db import journalListModel 
import datetime
import random
import json
import pytz

# 建立 Flask Blueprint
account_book_id = Blueprint("account_book_id", __name__)


@account_book_id.route("/api/account_book/<int:bookId>", methods=["GET", "POST", "DELETE", "PUT"])
def journal_list(bookId):
    # 取得日記帳明細
    if request.method == "GET":
        if "token"  not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403
  
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

        results = journalListModel.get_journal_lists(bookId, start_dt, end_dt)
        if not results:
            return jsonify({
                        "data" : "尚無新增項目"            
                    }),200
        if results == "INTERNAL_SERVER_ERROR":
            return jsonify({
                    "error": True,
                    "data" : "INTERNAL_SERVER_ERROR",             
                }),500
        
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



    # 建立日記帳
    if request.method == "POST":
        data = request.get_json()
        date = data["date"]
        category_main = data["category_main"]
        category_object = data["category_object"]
        category_character = data["category_character"]
        keyword = data["keyword"]
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
       
        taiwan_tz = pytz.timezone('Asia/Taipei')
        now_taiwan = datetime.datetime.now(taiwan_tz)
        created_time = now_taiwan.strftime('%Y%m%d%H%M%S')
        create_num = random.randrange(100,999)
        journal_list_id = created_time + str(create_num)
        status = "未結算"
        prepaid_dict = {item['collaborator_id']: item['price'] for item in prepaid}
        payable_dict = {item['collaborator_id']: item['price'] for item in payable}
        ids = set(prepaid_dict) | set(payable_dict)
        journal_list_price_value = [(journal_list_id, id, prepaid_dict.get(id, 0), payable_dict.get(id, 0)) for id in ids]
        result = journalListModel.create_journal_list(journal_list_id, date, amount, bookId, journal_list_price_value, category_main, category_object, category_character ,status , created_time, keyword)
        if result == "SUCCESS":
            return jsonify({
                        "ok": True,          
                    }),200
        if result == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500
        



    # 刪除日記帳
    if request.method == "DELETE":
        if "token" not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        data = request.get_json()
        id = data["id"]
        status = "未結算"
        result = journalListModel.delete_journal_list(id, status)
        if not result :
            return jsonify({
                    "data": "支出已結算，無法刪除。"    
                }),200
        if result == "SUCCESS":
            return jsonify({
                        "ok": True    
                    }),200
        if result == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500


    
    # 修改日記帳
    if request.method == "PUT":
        data = request.get_json()
        date = data["date"]
        category_main = data["category_main"]
        category_object = data["category_object"]
        category_character = data["category_character"]
        keyword = data["keyword"]
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
    
        status = "已結算"
        result = journalListModel.get_status_of_journal_list(journal_list_id, status)
        if result == "已結算":
            return jsonify({
                        "data": "支出已結算，無法編輯"    
                    }),200
        if result == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500
        taiwan_tz = pytz.timezone('Asia/Taipei')
        now_taiwan = datetime.datetime.now(taiwan_tz)
        modified_time = now_taiwan.strftime('%Y%m%d%H%M%S')
        prepaid_dict = {item['collaborator_id']: item['price'] for item in prepaid}
        payable_dict = {item['collaborator_id']: item['price'] for item in payable}
        ids = set(prepaid_dict) | set(payable_dict)
        journal_list_price_value = [( prepaid_dict.get(id, 0), payable_dict.get(id, 0), modified_time ,journal_list_id, id ) for id in ids]
        result = journalListModel.modify_journal_list(journal_list_id, date, amount, modified_time, bookId, journal_list_price_value, category_main, category_object, category_character, keyword)
        if result == "SUCCESS":
            return jsonify({
                        "ok": True,          
                    }),200
        if result == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500

       