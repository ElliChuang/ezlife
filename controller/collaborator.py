from flask import *
from model.user_db import userModel
from model.collaborator_db import collaboratorModel
import jwt
from config import TOKEN_PW

# 建立 Flask Blueprint
collaborator = Blueprint("collaborator", __name__)

@collaborator.route("/api/collaborator", methods=["POST", "DELETE"])
def set_collaborator():
    # 新增共同編輯者
    if request.method == "POST":
        data = request.get_json()
        email = data["email"]
        book_id = data["bookId"]
        if email == "" or book_id == "":
            return jsonify({
                        "error": True,
                        "data" : "請輸入信箱及帳簿編號",             
                    }),400

        if "token"  not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        token = session["token"]
        decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
        created_member_id = decode_data["id"]
        check_auth = collaboratorModel.check_edit_permission(created_member_id, book_id)
        if not check_auth:
            return jsonify({
                        "error": True,
                        "data" : "無新增權限，請洽帳簿管理員",             
                    }),403
        if check_auth == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500

        existing_user = userModel.get_user_by_email(email)
        if not existing_user:
            return jsonify({
                        "error": True,
                        "data" : "查無此會員",             
                    }),403
        if existing_user == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500
        
        collaborator_id = existing_user["id"]
        add_co_editor = collaboratorModel.add_collaborator(collaborator_id, book_id)
        if not add_co_editor:
            return jsonify({
                        "error": True, 
                        "data": "該會員已經是帳簿成員"     
                    }),403
        if add_co_editor == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500

        return jsonify({
                    "ok": True, 
                    "data": {
                        "name" : existing_user["name"]
                        }         
                }),200




    # 刪除共同編輯者
    if request.method == "DELETE":
        if "token"  not in session:
            return jsonify({
                        "error": True,
                        "data" : "請先登入會員",             
                    }),403

        data = request.get_json()
        collaborator_id = data["collaboratorId"]
        book_id = data["bookId"]
        token = session["token"]
        decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
        created_member_id = decode_data["id"]
        check_auth = collaboratorModel.check_edit_permission(created_member_id, book_id)
        if not check_auth:
            return jsonify({
                        "error": True,
                        "data" : "無刪除權限，請洽帳簿管理員",             
                    }),403
        if check_auth == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500
        delete_co_editor = collaboratorModel.delete_collaborator(collaborator_id, book_id)
        if delete_co_editor == "SUCCESS":
            return jsonify({
                        "ok": True    
                    }),200
        if delete_co_editor == "INTERNAL_SERVER_ERROR":
            return jsonify({
                        "error": True,
                        "data" : "INTERNAL_SERVER_ERROR",             
                    }),500
    