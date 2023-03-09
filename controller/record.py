from flask import *
from model.settle_db import SettleModel 

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

        account_dt = request.args.get("account_dt")
        status = "已結算"
        results = SettleModel.get_records(bookId, account_dt, status)
        if not results:
            return jsonify({
                        "data" : "無結算紀錄"             
                    }),200
        if results == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500
                
        dict = {}
        for i in results:
            key = i["account_dt"].strftime('%Y-%m-%d %H:%M:%S')
            if key not in dict:
                dict[key] = {
                            "account_dt" : key,
                            "account_member" : i["account_member"],
                            "records" : []
                        }
            record = {
                    "name": i["name"],
                    "payable" : i["payable"],
                    "prepaid": i["prepaid"]
                }

            dict[key]["records"].append(record)
        
        output = list(dict.values())
            
        return jsonify({
                    "ok" : True,
                    "data" : output             
                }),200
