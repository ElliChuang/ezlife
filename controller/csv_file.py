from flask import *
from model.analysis_db import analysisModel
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

    category_main = request.args.get("main")
    category_character = request.args.get("character")
    category_object = request.args.get("object")
    keyword = request.args.get("keyword")
    start_dt = ""
    end_dt = ""
    if month == 12:
        start_dt = f'{year}-{month}-01'
        end_dt = f'{year + 1}-01-01'
    else:
        start_dt = f'{year}-{month}-01'
        end_dt = f'{year}-{month + 1}-01'
    
    # 明細賬
    results_of_filtered = analysisModel.get_filtered_datas(bookId, start_dt, end_dt, category_main, category_character, category_object, keyword)
    if not results_of_filtered:
        journal_list = {"data": "查無帳目明細"}
        df = pd.DataFrame(journal_list, index = [0])
        df.to_csv(f'csv/data.csv', index = False)
        return send_from_directory('csv', 'data.csv', as_attachment=True)
    if results_of_filtered == "INTERNAL_SERVER_ERROR":
        return jsonify({
                    "error": True,
                    "data" : "INTERNAL_SERVER_ERROR",             
                }),500

    # respose data
    journal_list = []
    for item in results_of_filtered:
        date = item["date"].strftime('%Y-%m-%d')
        if item["keyword"]:
            data = {
                    "日期" : date,
                    "生活機能" : item["category_main"],
                    "消費型態" : item["category_object"],
                    "支出對象" : item["category_character"],
                    "關鍵字" : item["keyword"],
                    "金額" : item["amount"],
                }
        else:
            data = {
                    "日期" : date,
                    "生活機能" : item["category_main"],
                    "消費型態" : item["category_object"],
                    "支出對象" : item["category_character"],
                    "關鍵字" : "",
                    "金額" : item["amount"],
                }
        journal_list.append(data)

    # Generate a CSV file from the results
    df = pd.DataFrame(journal_list)
    df.to_csv(f'csv/data.csv', index = False)

    return send_from_directory('csv', 'data.csv', as_attachment=True)





    