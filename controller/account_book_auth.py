from flask import *
from model.book_db import BookModel 
import jwt
from config import TOKEN_PW

# 建立 Flask Blueprint
account_book_auth = Blueprint("account_book_auth", __name__)

@account_book_auth.route("/api/account_book_auth/<int:bookId>", methods=["GET"])
def book_auth(bookId):
    if "token" not in session:
        return jsonify({
                    "error": True,
                    "data" : "請先登入會員",             
                }),403

    token = session["token"]
    decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
    member_id = decode_data["id"]
    get_auth = BookModel.get_book_auth(bookId)
    if not get_auth:
        return jsonify({
                    "error": True,
                    "data" : "無帳簿權限",             
                }),403
    if get_auth == "INTERNAL_SERVER_ERROR":
        return jsonify({
                    "error": True,
                    "data" : "INTERNAL_SERVER_ERROR",             
                }),500
    
    for item in get_auth:
        if item['id'] == int(member_id):
            return jsonify({
                        "ok": True,
                        "data" : get_auth         
                    }),200
        else:
            continue
        
    return jsonify({
                    "error": True,
                    "data" : "無帳簿權限",             
                }),403

    