from flask import *
from model.book_db import bookModel
import jwt
from config import TOKEN_PW


# 建立 Flask Blueprint
account_books = Blueprint("account_books", __name__)

@account_books.route("/api/account_books", methods=["GET", "POST", "DELETE", "PUT"])
def book():
    # 取得帳簿資訊
    if request.method == "GET":
        if "token" not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403
  
        token = session["token"]
        decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
        member_id = decode_data["id"]
        books = bookModel.get_books_by_member(member_id)
        if not books: 
            return jsonify({
                        "data" : None
                    }),200
        if books == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500
        
        # respose data
        datas = []
        for item in books:
            data = {
                "account_book" : {
                    "id" : item["id"],
                    "book_name" : item["book_name"],
                    "created_member_id" : item["created_member_id"],
                },
            }
            datas.append(data)
        
        return jsonify({
                    "data": datas
                }),200

       

    # 建立帳簿
    if request.method == "POST":
        data = request.get_json()
        book_name = data["bookName"]
        if book_name == "":
            return jsonify({
                        "error": True,
                        "data" : "請輸入帳簿名稱",             
                    }),400

        if "token" not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        token = session["token"]
        decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
        created_member_id = decode_data["id"]
        
        # 確認帳簿名稱是否重複
        existing_book = bookModel.check_if_exist(book_name, created_member_id)
        if existing_book == "ALREADY EXIST":
            return jsonify({
                        "error": True,
                        "data" : "帳簿名稱已重複，請重新輸入",             
                    }),400
        if existing_book == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500

        new_book = bookModel.create_book(book_name, created_member_id) 
        if new_book == "SUCCESS":
            return jsonify({
                        "ok": True,          
                    }),200
        if new_book == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500



    # 刪除帳簿
    if request.method == "DELETE":
        if "token" not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        token = session["token"]
        data = request.get_json()
        book_id = data["bookId"]
        decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
        created_member_id = decode_data["id"]
        delete_book = bookModel.delete_book(created_member_id, book_id) 
        if not delete_book:
            return jsonify({
                    "error": True,
                    "data": "無刪除權限，請洽帳簿管理員"    
                }),400 
        if delete_book == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error" : True,
                        "data" : "INTERNAL_SERVER_ERROR"
                    }),500
        if delete_book == "SUCCESS":
            return jsonify({
                        "ok": True    
                    }),200



    # 修改帳簿名稱
    if request.method == "PUT":
        if "token" not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403
        
        data = request.get_json()
        book_name = data["bookName"]
        book_id = data["bookId"]
        if book_name == "":
            return jsonify({
                        "error": True,
                        "data" : "請輸入帳簿名稱",             
                    }),400

        token = session["token"]
        decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
        created_member_id = decode_data["id"]
        
        existing_book = bookModel.check_if_exist(book_name, created_member_id)
        if existing_book == "ALREADY EXIST":
            return jsonify({
                        "error": True,
                        "data" : "帳簿名稱已重複，請重新輸入",             
                    }),400
        if existing_book == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500
        
        update_book = bookModel.update_book(book_name, created_member_id, book_id)
        if not update_book:
            return jsonify({
                        "error": True,
                        "data": "無編輯權限，請洽帳簿管理員"    
                    }),400 
        if update_book == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500
        if update_book == "SUCCESS":
            return jsonify({
                        "ok": True,
                        "data":{
                            "book_name" : book_name,
                            "book_id" : book_id
                        }
                    }),200

