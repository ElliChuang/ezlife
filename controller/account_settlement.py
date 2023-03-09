from flask import *
from model.settle_db import SettleModel
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
        status = "未結算"
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

        overview = SettleModel.get_overview(bookId, start_dt, end_dt, status)
        if not overview:
            return jsonify({
                        "data" : "該月份無未結算項目"             
                    }),200
        if overview == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500

        results = SettleModel.get_journal_lists(bookId, start_dt, end_dt, status, collaborator_id)
        if not results:
            return jsonify({
                        "data" : "該月份無未結算項目"        
                    }),200
        if results == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500

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
        
        token = session["token"]
        decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
        member_id = decode_data["id"]
        member_name = decode_data["name"]
        taiwan_tz = pytz.timezone('Asia/Taipei')
        now_taiwan = datetime.datetime.now(taiwan_tz)
        account_dt = now_taiwan.strftime('%Y%m%d%H%M%S')
        result = SettleModel.settle_account(bookId, start_dt, end_dt, member_id, account_dt) 
        if result == "SUCCESS":
            return jsonify({
                        "ok": True,
                        "data":{
                            "collaborator_id": member_id,
                            "collaborator_name" : member_name
                        }          
                    }),200
        if result == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500


     
            



   