from flask import *
from werkzeug.security import check_password_hash
from model.user_db import userModel
import jwt
import datetime
import boto3
from PIL import Image
from config import TOKEN_PW, S3_ACCESS_KEY_ID, S3_ACCESS_SECRET_KEY, CLOUDFRONT_PATH, S3_BUCKET_NAME

# 建立 Flask Blueprint
user_auth = Blueprint("user_auth", __name__)

# 設定 s3
s3 = boto3.client('s3',
                    aws_access_key_id = S3_ACCESS_KEY_ID,
                    aws_secret_access_key= S3_ACCESS_SECRET_KEY,
                )

@user_auth.route("/api/user/auth", methods=["GET", "POST", "DELETE"])
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
								"profile" : decode_data["profile"]
							}
						}),200
			except:
				return jsonify({"data": "token is not valid."}),400
		else:
			return jsonify({"data": None}),400

	# 使用者登入
	if request.method == "POST":
		data = request.get_json()
		email = data["email"]
		password = data["password"]
		if email == "" or password == "":
			return jsonify({
						"error": True,
						"data" : "請輸入電子郵件及密碼",             
					}),400

		existing_user = userModel.get_user_by_email(email)
		if not existing_user: 
			return jsonify({
						"error": True,
						"data" : "電子郵件輸入錯誤",             
					}),400
		
		if existing_user == "INTERNAL_SERVER_ERROR":
			return jsonify({
				"error" : True,
				"data" : "INTERNAL_SERVER_ERROR"
			})
		
		if check_password_hash(existing_user["password"], password):
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
		else:
			return jsonify({
						"error": True,
						"data" : "密碼輸入錯誤",             
					}),400


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


# 修改會員資料
@user_auth.route("/api/user/auth", methods=["PATCH"])
def user_modify():
	id = request.form["memberId"]
	name = request.form["memberName"]
	email = request.form["memberEmail"]
	image = request.files.get('file')
	if not name or not email:
		return jsonify({
					"error": True,
					"data" : "請輸入姓名及電子郵件",             
				}),400
	
	# 使用者未更新大頭照
	if not image:
		profile = request.form["profile"]
		update_user = userModel.update_user_without_profile(name, email, id)
		if update_user == "SUCCESS":
			# 更新 token 資料
			payload = {
						"id" : id,
						"name" : name,
						"email" : email,
						"profile" : profile,
						'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=3)
					}
			token = jwt.encode(payload, TOKEN_PW, algorithm="HS256")
			session["token"] = token
			return jsonify({
						"ok" : True,
						"data":{
							"id" : id,
							"name" : name,
							"email" : email,
							"profile" : profile
						}
					})
		else:
			return jsonify({
						"error" : True,
						"data" : "INTERNAL_SERVER_ERROR"
					})


	# 使用者有更新大頭照
	allow_file_type = {'png', 'jpg', 'jpeg'}
	file_type = image.content_type.split("/")[1]
	if file_type not in allow_file_type:
		return jsonify({
					"error": True,
					"data" : "圖片格式有誤",             
				}),400

	img = Image.open(image)
	width = img.width
	height = img.height
	if width < 300 or height < 300:
		return jsonify({
					"error": True,
					"data" : "圖片寬高低於 300 像素",             
				}),400

	# resize image
	img.thumbnail((500,500), Image.Resampling.LANCZOS)
	rgb_img = img.convert('RGBA')
	rgb_img.save('static/img/profile.png')
	now = datetime.datetime.now()
	time = now.strftime("%m/%d/%Y-%H:%M:%S")
	unique_filename = "profile.png" + "/" + time 

	# 圖片存 S3
	with open('static/img/profile.png', 'rb') as file:
		s3.upload_fileobj(file, S3_BUCKET_NAME, 'profile/' + unique_filename)
		profile = f'https://{CLOUDFRONT_PATH}/profile/{unique_filename}'

	# 圖片 CDN 網址及會員資料更新到 RDS
	update_user = userModel.update_user_with_profile(name, email, profile, id)
	if update_user == "SUCCESS":
		# 更新 token 資料
		payload = {
					"id" : id,
					"name" : name,
					"email" : email,
					"profile" : profile,
					'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=3)
				}
		token = jwt.encode(payload, TOKEN_PW, algorithm="HS256")
		session["token"] = token
		return jsonify({
					"ok" : True,
					"data":{
						"id" : id,
						"name" : name,
						"email" : email,
						"profile" : profile
					}
				})
	else:
		return jsonify({
					"error" : True,
					"data" : "INTERNAL_SERVER_ERROR"
				})

