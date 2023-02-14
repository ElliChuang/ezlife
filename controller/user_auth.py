from flask import *
from mysql.connector import errorcode
import mysql.connector 
from werkzeug.security import generate_password_hash, check_password_hash
from model.db import MySQL 
import jwt
import datetime
import secrets
from google.oauth2 import id_token
from google.auth.transport import requests
from config import TOKEN_PW, GOOGLE_OAUTH2_CLIENT_ID

# 建立 Flask Blueprint
user_auth = Blueprint("user_auth", __name__)

@user_auth.route("/api/user", methods=["POST"])
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
			query = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
			value = (data["name"], data["email"], hash_password)
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


@user_auth.route("/api/user/auth", methods=["GET", "PUT", "DELETE"])
def user():
	# 取得當前會員資訊
	if request.method == "GET":
		if "token" in session:
			try:
				token = session["token"]
				decode_data = jwt.decode(token, TOKEN_PW, algorithms="HS256")
				return jsonify({
						"data": {
								"id" : decode_data["id"],
								"name" : decode_data["name"],
								"email" : decode_data["email"],
							}
						}),200
			except:
				return jsonify({"data": "token is not valid."})
		else:
			return jsonify({"data": None}),400

	# 使用者登入
	if request.method == "PUT":
		data = request.get_json()
		email = data["email"]
		password = data["password"]
		if email == "" or password == "":
			return jsonify({
						"error": True,
						"data" : "請輸入電子郵件及密碼",             
					}),400
		try:
			connection_object = MySQL.conn_obj()
			mycursor = connection_object.cursor(dictionary=True)
			query = ("SELECT id, name, email, password FROM member WHERE email = %s")
			mycursor.execute(query, (email,))
			result = mycursor.fetchone()
			if not result: 
				return jsonify({
							"error": True,
							"data" : "電子郵件輸入錯誤",             
						}),400
			elif check_password_hash(result["password"], password):
				payload = {
					"id" : result["id"],
					"name" : result["name"],
					"email" : result["email"],
					'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=3)
				}
				token = jwt.encode(payload, TOKEN_PW, algorithm="HS256")
				session["token"] = token
				return jsonify({
							"ok": True    
						}),200
			else:
				return jsonify({
							"error": True,
							"data" : "密碼輸入錯誤",             
						}),400

		except mysql.connector.Error as err:
			print("Something went wrong when user login: {}".format(err))
			return jsonify({
				"error": True,
				"data" : "INTERNAL_SERVER_ERROR",             
			}),500

		finally:
			if connection_object.is_connected():
				mycursor.close()
				connection_object.close()


	# 登出會員
	if request.method == "DELETE":
		try:
			session.pop("token", None)
			return jsonify({
						"ok": True    
					}),200
		except:
			return  jsonify({
						"error": True,
						"data" : "INTERNAL_SERVER_ERROR",             
					}),500



@user_auth.route("/api/user/auth", methods=["POST"])
def google_login():
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
			query = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
			value = (name, email, password)
			mycursor.execute(query, value)
			connection_object.commit() 

			# 取得 user id
			user_id = mycursor.lastrowid
			user = {
				"id" : user_id,
				"name" : name,
				"email" : email
			}

		payload = {
					"id" : user["id"],
					"name" : user["name"],
					"email" : user["email"],
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