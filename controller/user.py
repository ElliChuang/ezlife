from flask import *
from werkzeug.security import generate_password_hash
from model.user_db import UserModel 
import jwt
import datetime
import secrets
from google.oauth2 import id_token
from google.auth.transport import requests
from config import TOKEN_PW, GOOGLE_OAUTH2_CLIENT_ID

# 建立 Flask Blueprint
user = Blueprint("user", __name__)


@user.route("/api/user", methods=["POST"])
def signup():
	data = request.get_json()
	if data["name"] == "" or data["email"] == "" or data["password"] == "":
		return jsonify({
					"error": True,
					"data" : "請輸入姓名、電子郵件及密碼",             
				}),400

	existing_user = UserModel.get_user_by_email(data["email"])
	if not existing_user:
		# 將使用者密碼加密
		hash_password = generate_password_hash(data['password'], method='sha256')
		initial_profile = 'https://d12sr6yglyx2x4.cloudfront.net/profile/user+(2023.03.05).png'
		user_id = UserModel.create_user(data["name"], data["email"], hash_password, initial_profile)
		payload = {
				"id" : user_id,
				"name" : data["name"],
				"email" : data["email"],
				"profile" : initial_profile,
				'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=3)
			}
		token = jwt.encode(payload, TOKEN_PW, algorithm="HS256")
		session["token"] = token

		return jsonify({
					"ok": True,          
				}),200
	
	if existing_user == "INTERNAL_SERVER_ERROR":
		return jsonify({
			"error" : True,
			"data" : "INTERNAL_SERVER_ERROR"
		})
	
	if existing_user["email"]:
		return jsonify({
					"error": True,
					"data" : "電子郵件已被註冊",             
				}),400


@user.route("/api/user", methods=["PUT"])
def google_user():
	data = request.get_json()
	credential = data["credential"]
	try:
		idinfo = id_token.verify_oauth2_token(credential, requests.Request(), GOOGLE_OAUTH2_CLIENT_ID)
		email = idinfo["email"]
		name = idinfo["name"]

	except ValueError:
		return jsonify({"error": True, "data": "Invalid token"})

	# 確認使用者是否已經註冊過
	existing_user = UserModel.get_user_by_email(email)
	if not existing_user:
		password = secrets.token_hex(16)
		initial_profile = 'https://d12sr6yglyx2x4.cloudfront.net/profile/user+(2023.03.05).png'
		user_id = UserModel.create_user(name, email, password, initial_profile) 
		if user_id == "INTERNAL_SERVER_ERROR":
			return jsonify({
				"error" : True,
				"data" : "INTERNAL_SERVER_ERROR"
			})
		existing_user = {
			"id" : user_id,
			"name" : name,
			"email" : email,
			"profile" : initial_profile
		}

	if existing_user == "INTERNAL_SERVER_ERROR":
		return jsonify({
			"error" : True,
			"data" : "INTERNAL_SERVER_ERROR"
		})

	payload = {
				"id" : existing_user["id"],
				"name" : existing_user["name"],
				"email" : existing_user["email"],
				"profile" : existing_user["profile"],
				'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=3)
			}
	token = jwt.encode(payload, TOKEN_PW, algorithm="HS256")
	session["token"] = token
	return jsonify({
				"ok": True    
			}),200





