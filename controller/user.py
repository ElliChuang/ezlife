from flask import *
from mysql.connector import errorcode
import mysql.connector 
from werkzeug.security import generate_password_hash
from model.db import MySQL 
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
	try:
		connection_object = MySQL.conn_obj()
		mycursor = connection_object.cursor()
		query = ("SELECT email FROM member where email = %s")
		mycursor.execute(query, (data["email"],))
		result = mycursor.fetchone()
		if result:
			return jsonify({
						"error": True,
						"data" : "電子郵件已被註冊",             
					}),400
		else: 
			# 將使用者密碼加密
			hash_password = generate_password_hash(data['password'], method='sha256')
			initial_profile = 'https://d12sr6yglyx2x4.cloudfront.net/profile/cow.png(02/17/2023-12:32:06)'
			query = "INSERT INTO member (name, email, password, profile) VALUES (%s, %s, %s, %s)"
			value = (data["name"], data["email"], hash_password, initial_profile)
			mycursor.execute(query, value)
			connection_object.commit() 
			return jsonify({
						"ok": True,          
					}),200

	except mysql.connector.Error as err:
		print("Something went wrong when user sign up: {}".format(err))
		return jsonify({
					"error": True,
					"data" : "INTERNAL_SERVER_ERROR",             
				}),500

	finally:
		if connection_object.is_connected():
			mycursor.close()
			connection_object.close()




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
	try:
		connection_object = MySQL.conn_obj()
		mycursor = connection_object.cursor(dictionary=True)
		query = ("SELECT * FROM member WHERE email = %s")
		mycursor.execute(query, (email,))
		user = mycursor.fetchone()

		if not user:
			# 未註冊，將會員資料建入資料庫
			password = secrets.token_hex(16)
			initial_profile = 'https://d12sr6yglyx2x4.cloudfront.net/profile/cow.png(02/17/2023-12:32:06)'
			query = "INSERT INTO member (name, email, password, profile) VALUES (%s, %s, %s, %s)"
			value = (name, email, password, initial_profile)
			mycursor.execute(query, value)
			connection_object.commit() 

			# 取得 user id
			user_id = mycursor.lastrowid
			user = {
				"id" : user_id,
				"name" : name,
				"email" : email,
				"profile" : initial_profile
			}

		payload = {
					"id" : user["id"],
					"name" : user["name"],
					"email" : user["email"],
					"profile" : user["profile"],
					'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=3)
				}
		token = jwt.encode(payload, TOKEN_PW, algorithm="HS256")
		session["token"] = token

		return jsonify({
					"ok": True    
				}),200

	except mysql.connector.Error as err:
			print("Something went wrong when use google login: {}".format(err))
			return jsonify({
				"error": True,
				"data" : "INTERNAL_SERVER_ERROR",             
			}),500

	finally:
		if connection_object.is_connected():
			mycursor.close()
			connection_object.close()



