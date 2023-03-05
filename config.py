import os
from dotenv import load_dotenv
load_dotenv()

MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PW = os.environ.get("MYSQL_PW")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
REDIS_HOST = os.environ.get("REDIS_HOST")
TOKEN_PW = os.environ.get("TOKEN_PW")
SECRET_KEY = os.environ.get("SECRET_KEY")
GOOGLE_OAUTH2_CLIENT_ID = os.environ.get("GOOGLE_OAUTH2_CLIENT_ID")
S3_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY_ID")
S3_ACCESS_SECRET_KEY = os.environ.get("S3_ACCESS_SECRET_KEY")

JSON_AS_ASCII = False
TEMPLATES_AUTO_RELOAD = True
JSON_SORT_KEYS = False

CLOUDFRONT_PATH = 'd12sr6yglyx2x4.cloudfront.net'
S3_BUCKET_NAME = 'week1bucket'