from flask import *
from model.analysis_db import analysisModel

# 建立 Flask Blueprint
chart = Blueprint("chart", __name__)

@chart.route("/api/account_book/<int:bookId>/chart", methods=["GET"])
def chart_data(bookId):
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
    
    # 圓餅圖
    results_of_pipe = analysisModel.get_pipe(bookId, start_dt, end_dt)
    if results_of_pipe == "INTERNAL_SERVER_ERROR":
        return jsonify({
                    "error": True,
                    "data" : "INTERNAL_SERVER_ERROR",             
                }),500

    chart_main = {"食":0, "衣":0, "住":0, "行":0, "育":0, "樂":0}
    chart_character = {"個人":0, "家庭":0, "育兒":0, "寵物":0,"宿舍":0, "旅行":0}
    for item in results_of_pipe:
        if item["category"] in chart_main:
            chart_main[item["category"]] = int(item["amount"])
        if item["category"] in chart_character:   
            chart_character[item["category"]] = int(item["amount"])
    
    # 明細賬
    results_of_filtered = analysisModel.get_filtered_datas(bookId, start_dt, end_dt, category_main, category_character, category_object, keyword)
    if not results_of_filtered:
        return jsonify({
                    "query_year" : year,
                    "query_month" : month,
                    "chart_main" : chart_main,
                    "chart_character" : chart_character,
                    "journal_list": "查無帳目明細"          
                }),200
    if results_of_filtered == "INTERNAL_SERVER_ERROR":
        return jsonify({
                    "error": True,
                    "data" : "INTERNAL_SERVER_ERROR",             
                }),500

    # respose data
    journal_list = []
    journal_list_main={"食":0, "衣":0, "住":0, "行":0, "育":0, "樂":0}
    for item in results_of_filtered:
        date = item["date"].strftime('%Y-%m-%d')
        day = item["date"].strftime('%a')
        if item["keyword"]:
            data = {
                    "journal_list" : {
                        "id" : item["id"],
                        "date" : date,
                        "day" : day,
                        "category_main" : item["category_main"],
                        "category_object" : item["category_object"],
                        "category_character" : item["category_character"],
                        "keyword" : item["keyword"],
                        "price" : item["amount"],
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
                        "keyword" : "",
                        "price" : item["amount"],
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




    